"""
MongoDB data-access layer (repository pattern) for Lawmate.

Contains typed helpers for citizens, lawyers, admins, stored cases, lawyer–client
rows, chat history, and platform settings. All functions use ``get_collection``
from ``db.database`` and strip ``_id`` where API responses should stay JSON-clean.

Transient network errors to MongoDB Atlas are retried in hot paths via
``_run_with_mongo_retry``.
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, TypeVar

from passlib.context import CryptContext
from pymongo import ReturnDocument
from pymongo.errors import AutoReconnect, NetworkTimeout, ServerSelectionTimeoutError

from .database import get_collection, get_database

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
T = TypeVar("T")

DEFAULT_ADMIN_SETTINGS: Dict[str, Any] = {
    "platform_name": "Lawmate",
    "support_email": "support@justiceai.com",
    "max_file_upload_size_mb": 50,
    "email_notifications": True,
    "ai_monitoring": True,
    "auto_backup": True,
    "maintenance_mode": False,
}


def init_schema() -> None:
    # MongoDB is schemaless; ensure indexes for common unique lookups.
    get_collection("citizens").create_index("email", unique=True)
    get_collection("lawyers").create_index("email", unique=True)
    get_collection("stored_cases").create_index([("scope", 1), ("id", 1)])
    get_collection("admin_users").create_index("email", unique=True)
    get_collection("app_settings").create_index("key", unique=True)
    get_collection("lawyer_client_rows").create_index([("lawyer_id", 1), ("client_id", 1)])
    get_collection("chat_messages").create_index([("session_id", 1), ("created_at", -1)])
    get_collection("chat_messages").create_index([("user_id", 1), ("created_at", -1)])


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _strip_id(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not doc:
        return None
    clean = dict(doc)
    clean.pop("_id", None)
    return clean


def _find_user_by_login_email(collection: str, email: str) -> Optional[Dict[str, Any]]:
    """Match stored email: signups use lowercase; fall back to exact strip for legacy rows."""
    raw = (email or "").strip()
    if not raw:
        return None
    lowered = raw.lower()
    c = _strip_id(get_collection(collection).find_one({"email": lowered}))
    if c:
        return c
    if raw != lowered:
        return _strip_id(get_collection(collection).find_one({"email": raw}))
    return None


def _run_with_mongo_retry(fn: Callable[[], T], *, attempts: int = 4, base_delay_sec: float = 0.35) -> T:
    """
    Retry transient Mongo connectivity errors so brief Atlas hiccups don't fail user operations.
    """
    last_err: Optional[Exception] = None
    for i in range(attempts):
        try:
            return fn()
        except (AutoReconnect, NetworkTimeout, ServerSelectionTimeoutError) as err:
            last_err = err
            if i == attempts - 1:
                break
            sleep_s = base_delay_sec * (2 ** i)
            time.sleep(sleep_s)
    if last_err:
        raise last_err
    raise RuntimeError("Mongo retry failed with unknown error")


def _citizen_public(c: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": c.get("id", ""),
        "name": c.get("name", ""),
        "email": c.get("email", ""),
        "role": "Citizen",
        "joinDate": c.get("join_date", ""),
        "status": c.get("status", "Active"),
        "casesInvolved": int(c.get("cases_involved", 0) or 0),
    }


def _lawyer_public(l: Dict[str, Any]) -> Dict[str, Any]:
    specs = l.get("specializations", [])
    if not isinstance(specs, list):
        specs = []
    return {
        "id": l.get("id", ""),
        "name": l.get("name", ""),
        "email": l.get("email", ""),
        "specialization": l.get("specialization", "General Practice"),
        "verificationStatus": l.get("verification_status", "Pending"),
        "casesSolved": int(l.get("cases_solved", 0) or 0),
        "winRate": float(l.get("win_rate", 0) or 0),
        "joinDate": l.get("join_date", ""),
        "location": l.get("location", "Not specified"),
        "rating": float(l.get("rating", 0) or 0),
        "reviews": int(l.get("reviews", 0) or 0),
        "specializations": specs,
        "yearsExp": int(l.get("years_exp", 0) or 0),
        "cases": int(l.get("cases", 0) or 0),
        "phone": l.get("phone", ""),
        "bio": l.get("bio", ""),
        "profileImage": l.get("profile_image", ""),
    }


# --- Citizens ---
def verify_citizen_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    c = _find_user_by_login_email("citizens", email)
    if not c or not verify_password(password, c.get("password_hash", "")):
        return None
    return _citizen_public(c)


def list_all_citizens_public() -> List[Dict[str, Any]]:
    rows = get_collection("citizens").find({}, {"_id": 0}).sort("email", 1)
    return [_citizen_public(r) for r in rows]


def create_citizen_record(
    name: str,
    email: str,
    password_plain: str,
    join_date: str,
    status: str = "Active",
    cases_involved: int = 0,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    if email_exists_as_citizen_or_lawyer(email):
        raise ValueError("Email already registered")
    uid = user_id or str(uuid.uuid4())[:8]
    doc = {
        "id": uid,
        "name": name,
        "email": email,
        "password_hash": hash_password(password_plain),
        "join_date": join_date,
        "status": status,
        "cases_involved": int(cases_involved),
    }
    get_collection("citizens").insert_one(doc)
    return _citizen_public(doc)


def update_citizen_by_id(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    set_doc: Dict[str, Any] = {}
    if "name" in updates and updates["name"] is not None:
        set_doc["name"] = updates["name"]
    if "email" in updates and updates["email"] is not None:
        set_doc["email"] = updates["email"]
    if "status" in updates and updates["status"] is not None:
        set_doc["status"] = updates["status"]
    if "joinDate" in updates and updates["joinDate"] is not None:
        set_doc["join_date"] = updates["joinDate"]
    if "casesInvolved" in updates and updates["casesInvolved"] is not None:
        set_doc["cases_involved"] = int(updates["casesInvolved"])
    if "password" in updates and updates["password"]:
        set_doc["password_hash"] = hash_password(str(updates["password"]))
    if not set_doc:
        doc = _strip_id(get_collection("citizens").find_one({"id": user_id}))
        return _citizen_public(doc) if doc else None
    res = get_collection("citizens").find_one_and_update(
        {"id": user_id},
        {"$set": set_doc},
        return_document=ReturnDocument.AFTER,
    )
    doc = _strip_id(res)
    return _citizen_public(doc) if doc else None


def delete_citizen_by_id(user_id: str) -> bool:
    res = get_collection("citizens").delete_one({"id": user_id})
    return res.deleted_count > 0


# --- Lawyers ---
def verify_lawyer_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    l = _find_user_by_login_email("lawyers", email)
    if not l or not verify_password(password, l.get("password_hash", "")):
        return None
    return _lawyer_public(l)


def list_all_lawyers_public() -> List[Dict[str, Any]]:
    rows = get_collection("lawyers").find({}, {"_id": 0}).sort("email", 1)
    return [_lawyer_public(r) for r in rows]


def lawyer_exists(lawyer_id: str) -> bool:
    return get_collection("lawyers").find_one({"id": lawyer_id}, {"_id": 1}) is not None


def create_lawyer_record(new_lawyer_dict: Dict[str, Any], password_plain: str) -> Dict[str, Any]:
    if email_exists_as_citizen_or_lawyer(new_lawyer_dict["email"]):
        raise ValueError("Email already exists")
    specs = new_lawyer_dict.get("specializations") or []
    if not isinstance(specs, list):
        specs = []
    doc = {
        "id": new_lawyer_dict["id"],
        "name": new_lawyer_dict.get("name", ""),
        "email": new_lawyer_dict["email"],
        "password_hash": hash_password(password_plain),
        "specialization": new_lawyer_dict.get("specialization", "General Practice"),
        "verification_status": new_lawyer_dict.get("verificationStatus", "Pending"),
        "cases_solved": int(new_lawyer_dict.get("casesSolved", 0) or 0),
        "win_rate": float(new_lawyer_dict.get("winRate", 0) or 0),
        "join_date": new_lawyer_dict.get("joinDate", ""),
        "location": new_lawyer_dict.get("location", "Not specified"),
        "rating": float(new_lawyer_dict.get("rating", 0) or 0),
        "reviews": int(new_lawyer_dict.get("reviews", 0) or 0),
        "specializations": specs,
        "years_exp": int(new_lawyer_dict.get("yearsExp", 0) or 0),
        "cases": int(new_lawyer_dict.get("cases", new_lawyer_dict.get("casesSolved", 0)) or 0),
        "phone": new_lawyer_dict.get("phone", ""),
        "bio": new_lawyer_dict.get("bio", ""),
        "profile_image": new_lawyer_dict.get("profileImage", ""),
    }
    get_collection("lawyers").insert_one(doc)
    return _lawyer_public(doc)


def update_lawyer_by_id(lawyer_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if "email" in updates and updates["email"]:
        existing = _strip_id(get_collection("lawyers").find_one({"email": updates["email"]}))
        if existing and existing.get("id") != lawyer_id:
            raise ValueError("Email already exists")

    field_map = {
        "name": "name",
        "email": "email",
        "specialization": "specialization",
        "verificationStatus": "verification_status",
        "casesSolved": "cases_solved",
        "winRate": "win_rate",
        "joinDate": "join_date",
        "location": "location",
        "rating": "rating",
        "reviews": "reviews",
        "yearsExp": "years_exp",
        "cases": "cases",
        "phone": "phone",
        "bio": "bio",
        "profileImage": "profile_image",
    }
    set_doc: Dict[str, Any] = {}
    for api_key, mongo_key in field_map.items():
        if api_key in updates and updates[api_key] is not None:
            set_doc[mongo_key] = updates[api_key]
    if "specializations" in updates and updates["specializations"] is not None:
        set_doc["specializations"] = updates["specializations"]
    if "casesSolved" in updates and updates["casesSolved"] is not None:
        set_doc["cases"] = int(updates["casesSolved"])
    if "password" in updates and updates["password"]:
        set_doc["password_hash"] = hash_password(str(updates["password"]))
    if not set_doc:
        doc = _strip_id(get_collection("lawyers").find_one({"id": lawyer_id}))
        return _lawyer_public(doc) if doc else None
    doc = _strip_id(
        get_collection("lawyers").find_one_and_update(
            {"id": lawyer_id},
            {"$set": set_doc},
            return_document=ReturnDocument.AFTER,
        )
    )
    return _lawyer_public(doc) if doc else None


def set_lawyer_verification_status(lawyer_id: str, status: str) -> Optional[Dict[str, Any]]:
    return update_lawyer_by_id(lawyer_id, {"verificationStatus": status})


def delete_lawyer_by_id(lawyer_id: str) -> bool:
    res = get_collection("lawyers").delete_one({"id": lawyer_id})
    return res.deleted_count > 0


def update_lawyer_profile_image(lawyer_id: str, image_url: str) -> Optional[Dict[str, Any]]:
    return update_lawyer_by_id(lawyer_id, {"profileImage": image_url})


# --- Stored cases ---
def append_stored_case(scope: str, case_dict: Dict[str, Any]) -> None:
    cid = case_dict.get("id")
    if not cid:
        raise ValueError("case dict must include id")
    def _write() -> None:
        get_collection("stored_cases").update_one(
            {"id": str(cid)},
            {"$set": {"id": str(cid), "scope": scope, "payload": case_dict}},
            upsert=True,
        )

    _run_with_mongo_retry(_write)


def list_stored_cases(scope: str) -> List[Dict[str, Any]]:
    rows = get_collection("stored_cases").find({"scope": scope}, {"_id": 0, "payload": 1})
    return [dict(r.get("payload", {})) for r in rows if isinstance(r.get("payload"), dict)]


def count_stored_cases(scope: str) -> int:
    return int(get_collection("stored_cases").count_documents({"scope": scope}))


# --- Lawyer client rows ---
def _payload_to_row_dict(payload: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(payload)
    d.pop("_row_id", None)
    return d


def list_lawyer_client_payloads(lawyer_id: Optional[str] = None) -> List[Dict[str, Any]]:
    query: Dict[str, Any] = {}
    if lawyer_id:
        query["lawyer_id"] = lawyer_id
    rows = get_collection("lawyer_client_rows").find(query, {"_id": 0})
    out: List[Dict[str, Any]] = []
    for r in rows:
        data = dict(r.get("payload", {}))
        if not isinstance(data, dict):
            continue
        data["_row_id"] = int(r.get("row_id", 0))
        out.append(data)
    return out


def append_lawyer_client_row(payload: Dict[str, Any]) -> None:
    clean = _payload_to_row_dict(payload)
    coll = get_collection("lawyer_client_rows")
    next_row = coll.count_documents({}) + 1
    coll.insert_one(
        {
            "row_id": next_row,
            "lawyer_id": str(clean.get("lawyerId") or ""),
            "client_id": str(clean.get("clientId") or ""),
            "payload": clean,
        }
    )


def get_entries_for_lawyer_client(lawyer_id: str, client_id: str) -> List[Dict[str, Any]]:
    rows = get_collection("lawyer_client_rows").find(
        {"lawyer_id": lawyer_id, "client_id": client_id},
        {"_id": 0},
    )
    out: List[Dict[str, Any]] = []
    for r in rows:
        data = dict(r.get("payload", {}))
        if not isinstance(data, dict):
            continue
        data["_row_id"] = int(r.get("row_id", 0))
        out.append(data)
    return out


def save_lawyer_client_entry(row_id: int, payload: Dict[str, Any]) -> None:
    clean = _payload_to_row_dict(payload)
    get_collection("lawyer_client_rows").update_one(
        {"row_id": int(row_id)},
        {
            "$set": {
                "lawyer_id": str(clean.get("lawyerId") or ""),
                "client_id": str(clean.get("clientId") or ""),
                "payload": clean,
            }
        },
    )


# --- Admin users / settings ---
def verify_admin_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    a = _find_user_by_login_email("admin_users", email)
    if not a or not verify_password(password, a.get("password_hash", "")):
        return None
    return {"id": a.get("id", "admin-1"), "name": a.get("name", "Admin User"), "email": a.get("email", ""), "role": "Admin", "userType": "admin"}


def get_admin_settings() -> Dict[str, Any]:
    row = _strip_id(get_collection("app_settings").find_one({"key": "admin_settings"}))
    merged = dict(DEFAULT_ADMIN_SETTINGS)
    if row and isinstance(row.get("value"), dict):
        merged.update(row["value"])
    return merged


def update_admin_settings_partial(updates: Dict[str, Any]) -> Dict[str, Any]:
    current = get_admin_settings()
    for k, v in updates.items():
        if v is not None:
            current[k] = v
    get_collection("app_settings").update_one(
        {"key": "admin_settings"},
        {"$set": {"key": "admin_settings", "value": current}},
        upsert=True,
    )
    return current


def email_exists_as_citizen_or_lawyer(email: str) -> bool:
    if get_collection("citizens").find_one({"email": email}, {"_id": 1}):
        return True
    if get_collection("lawyers").find_one({"email": email}, {"_id": 1}):
        return True
    return False


def get_lawyer_public_by_id(lawyer_id: str) -> Optional[Dict[str, Any]]:
    l = _strip_id(get_collection("lawyers").find_one({"id": lawyer_id}))
    return _lawyer_public(l) if l else None


def count_citizens() -> int:
    return int(get_collection("citizens").count_documents({}))


def count_lawyers() -> int:
    return int(get_collection("lawyers").count_documents({}))


def count_lawyers_with_verification(status: str) -> int:
    return int(get_collection("lawyers").count_documents({"verification_status": status}))


def unique_client_count_for_lawyer(lawyer_id: str) -> int:
    rows = list_lawyer_client_payloads(lawyer_id)
    return len({r.get("clientId") for r in rows if r.get("clientId")})


def find_stored_case_by_id(case_id: str) -> Optional[Dict[str, Any]]:
    row = _strip_id(get_collection("stored_cases").find_one({"id": case_id}, {"_id": 0, "payload": 1}))
    if not row:
        return None
    payload = row.get("payload")
    return dict(payload) if isinstance(payload, dict) else None


# --- Chat messages ---
def append_chat_message(
    *,
    session_id: str,
    role: str,
    content: str,
    user_id: Optional[str] = None,
    user_type: Optional[str] = None,
) -> None:
    if not session_id or not role or not content:
        return

    def _write() -> None:
        get_collection("chat_messages").insert_one(
            {
                "session_id": str(session_id),
                "role": str(role),
                "content": str(content),
                "user_id": str(user_id or ""),
                "user_type": str(user_type or ""),
                "created_at": time.time(),
            }
        )

    _run_with_mongo_retry(_write)


def list_recent_chat_messages(
    *,
    session_id: str,
    limit: int = 12,
) -> List[Dict[str, Any]]:
    if not session_id:
        return []
    rows = get_collection("chat_messages").find(
        {"session_id": str(session_id)},
        {"_id": 0, "role": 1, "content": 1, "created_at": 1},
    ).sort("created_at", -1).limit(max(1, int(limit)))
    # Return oldest -> newest for prompt readability.
    out = list(rows)
    out.reverse()
    return [dict(r) for r in out]
