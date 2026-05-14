"""
Fixed Advanced Web Scraper for Sindh High Court Criminal Cases
Targets https://caselaw.shc.gov.pk/caselaw/pview.php?rpt=search
Downloads PDFs + metadata → JSON
"""

import os
import re
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
import fitz  # PyMuPDF
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from tqdm import tqdm


class SHCCriminalScraper:
    BASE_URL = "https://caselaw.shc.gov.pk/caselaw/pview.php?rpt=search"

    # Fixed: Match exact text from HTML select options
    CRIMINAL_CATEGORIES = [
        "Cr.Rev",
        "Cr.J.A",
        "Cr.Ref",
        "Cr.Misc."
    ]

    def __init__(
        self,
        output_dir: str = "./data/shc_criminal",
        headless: bool = True,
        wait_timeout: int = 30,
        throttle_sec: float = 2.0,
    ):
        self.output_dir = output_dir
        self.pdf_dir = os.path.join(output_dir, "pdfs")
        self.json_dir = os.path.join(output_dir, "json")
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.StreamHandler()]
        )

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(90)
        except Exception as e:
            logging.error(f"Failed to initialize Chrome driver: {e}")
            raise

        self.wait = WebDriverWait(self.driver, wait_timeout)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.throttle_sec = throttle_sec

    # --------------- Public API ---------------

    def scrape(
        self,
        max_pages: Optional[int] = None,
        category: str = "Cr.Appeal",
        master_filename: Optional[str] = None
    ) -> List[Dict]:
        """Entry point: scrape the caselaw search with optional page cap."""
        logging.info("Opening SHC caselaw search form")
        
        try:
            self.driver.get(self.BASE_URL)
            time.sleep(4)  # Wait for page load
            logging.info("Page loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load search page: {e}")
            raise
        
        self._select_single_category(category)
        self._submit_form()

        all_cases = []
        page_no = 1

        while True:
            logging.info(f"Processing page {page_no}")
            cases_this_page = self._scrape_current_page()
            all_cases.extend(cases_this_page)

            if max_pages and page_no >= max_pages:
                logging.info(f"Reached max_pages limit: {max_pages}")
                break
            if not self._go_to_next_page():
                break
            page_no += 1
            time.sleep(self.throttle_sec)

        if master_filename is None:
            master_filename = f"shc_{self._slugify(category)}_cases.json"
        self._write_master_json(all_cases, master_filename)
        logging.info(f"Done. Total cases scraped: {len(all_cases)}")
        return all_cases

    def scrape_other_categories(
        self,
        skip_categories: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        combined_filename: str = "shc_criminal_other_categories.json"
    ) -> List[Dict]:
        """Scrape every criminal category except the ones provided."""
        skip = set(skip_categories or [])
        aggregated_cases: List[Dict] = []

        for category in self.CRIMINAL_CATEGORIES:
            if category in skip:
                logging.info(f"Skipping category (already scraped): {category}")
                continue

            logging.info(f"====== Scraping category: {category} ======")
            try:
                category_filename = f"shc_{self._slugify(category)}.json"
                cases = self.scrape(
                    max_pages=max_pages,
                    category=category,
                    master_filename=category_filename
                )
                aggregated_cases.extend(cases)
            except Exception as exc:
                logging.error(f"Failed scraping category {category}: {exc}")
                continue

        if aggregated_cases:
            self._write_master_json(aggregated_cases, combined_filename)
            logging.info(
                f"Combined JSON created with {len(aggregated_cases)} cases: {combined_filename}"
            )
        else:
            logging.warning("No cases scraped from the selected categories.")

        return aggregated_cases

    def close(self):
        try:
            self.driver.quit()
        except:
            pass
        try:
            self.session.close()
        except:
            pass

    # --------------- Page/Form Helpers ---------------

    def _select_single_category(self, category: str):
        """Select a single category from dropdown."""
        try:
            category_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "STD_CASETYPES"))
            )
            select = Select(category_element)

            try:
                select.select_by_visible_text(category)
                logging.info(f"Selected category: {category}")
                time.sleep(1)
            except NoSuchElementException:
                logging.error(f"Category not available: {category}")
                raise
                
        except Exception as e:
            logging.error(f"Error selecting category: {e}")
            raise

    def _submit_form(self):
        """Submit the search form."""
        try:
            # Find the specific search button with id="AdvanceSearch"
            logging.info("Looking for search button...")
            
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "AdvanceSearch"))
            )
            
            logging.info("Found search button, clicking...")
            
            # Scroll to button to ensure it's visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            time.sleep(1)
            
            # Click using JavaScript as backup
            try:
                submit_btn.click()
            except:
                logging.info("Regular click failed, using JavaScript click")
                self.driver.execute_script("arguments[0].click();", submit_btn)
            
            logging.info("Search button clicked, waiting for results...")
            
            # Wait longer for results to load (the page takes time)
            time.sleep(5)
            
            # Wait for results table to appear
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//table//tbody//tr"))
                )
                logging.info("Search results loaded successfully")
            except TimeoutException:
                # Check if "No records found" or still loading
                page_source = self.driver.page_source
                if "No record" in page_source or "No data" in page_source:
                    logging.warning("No records found for this search")
                else:
                    logging.warning("Results may still be loading...")
                    time.sleep(5)  # Wait extra time
                    
        except Exception as e:
            logging.error(f"Error submitting form: {e}")
            # Save screenshot for debugging
            try:
                self.driver.save_screenshot("error_screenshot.png")
                logging.info("Screenshot saved as error_screenshot.png")
            except:
                pass
            raise

    # --------------- Page Scraping ---------------

    def _scrape_current_page(self) -> List[Dict]:
        """Extract all cases from the current results page."""
        cases = []
        
        try:
            # Wait for table to fully load
            time.sleep(3)
            
            # Find all rows with PDF links
            # Look for green button links: <a href="view-file/...">
            pdf_buttons = self.driver.find_elements(
                By.XPATH, 
                "//a[contains(@href, 'view-file/')]"
            )
            
            logging.info(f"Found {len(pdf_buttons)} cases on this page")
            
            if len(pdf_buttons) == 0:
                logging.warning("No cases found on page. Checking page source...")
                # Debug: check if table exists
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                logging.info(f"Found {len(tables)} tables on page")
                return cases
            
            for idx in range(len(pdf_buttons)):
                try:
                    # Re-find elements to avoid stale reference
                    pdf_buttons = self.driver.find_elements(
                        By.XPATH, 
                        "//a[contains(@href, 'view-file/')]"
                    )
                    
                    if idx >= len(pdf_buttons):
                        break
                        
                    pdf_button = pdf_buttons[idx]
                    
                    # Get the case row
                    row = pdf_button.find_element(By.XPATH, "./ancestor::tr")
                    
                    # Extract metadata from row cells
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) < 4:
                        logging.warning(f"Row {idx} has insufficient cells: {len(cells)}")
                        continue
                    
                    # Parse case information from table cells
                    # Adjust indices based on actual table structure
                    try:
                        case_no = cells[3].text.strip() if len(cells) > 3 else ""
                        case_year = cells[4].text.strip() if len(cells) > 4 else ""
                        parties = cells[5].text.strip() if len(cells) > 5 else ""
                        bench = cells[6].text.strip() if len(cells) > 6 else ""
                        order_date = cells[7].text.strip() if len(cells) > 7 else ""
                    except Exception as e:
                        logging.warning(f"Error extracting cell data: {e}")
                        case_no = f"case_{idx}"
                        case_year = ""
                        parties = ""
                        bench = ""
                        order_date = ""
                    
                    # Generate case ID
                    case_id = self._generate_case_id(case_no, case_year, idx)
                    
                    # Get PDF URL from href
                    pdf_href = pdf_button.get_attribute("href")
                    logging.info(f"[{idx+1}/{len(pdf_buttons)}] Processing {case_id}")
                    
                    # Download PDF
                    if pdf_href:
                        pdf_path = self._download_case_pdf(pdf_href, case_id)
                        if pdf_path:
                            judgment_text = self._extract_pdf_text(pdf_path)
                        else:
                            judgment_text = ""
                    else:
                        logging.warning(f"No PDF URL found for case {case_id}")
                        pdf_path = None
                        judgment_text = ""
                    
                    metadata = {
                        "case_id": case_id,
                        "case_no": case_no,
                        "case_year": case_year,
                        "parties": parties,
                        "bench": bench,
                        "order_date": order_date,
                        "pdf_url": pdf_href,
                        "pdf_path": pdf_path,
                        "judgment_text": judgment_text,
                        "sections": self._extract_ppc_sections(judgment_text),
                        "scraped_at": datetime.utcnow().isoformat()
                    }
                    
                    cases.append(metadata)
                    self._write_case_json(metadata)
                    
                    time.sleep(self.throttle_sec / 2)
                    
                except StaleElementReferenceException:
                    logging.warning(f"Stale element at index {idx}, continuing...")
                    continue
                except Exception as e:
                    logging.error(f"Error processing case {idx}: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error scraping page: {e}")
        
        return cases

    def _go_to_next_page(self) -> bool:
        """Navigate to next page of results."""
        try:
            # Look for Next link/button
            next_elements = self.driver.find_elements(
                By.XPATH,
                "//a[contains(text(), 'Next')] | //button[contains(text(), 'Next')] | //li[contains(@class, 'next')]/a"
            )
            
            if not next_elements:
                logging.info("No Next button found - no more pages")
                return False
            
            next_btn = next_elements[0]
            
            # Check if disabled
            classes = next_btn.get_attribute("class") or ""
            parent_classes = next_btn.find_element(By.XPATH, "./..").get_attribute("class") or ""
            
            if "disabled" in classes or "disabled" in parent_classes:
                logging.info("Next button is disabled - no more pages")
                return False
            
            logging.info("Navigating to next page...")
            
            # Try clicking
            try:
                next_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", next_btn)
            
            time.sleep(4)  # Wait for page to load
            
            return True
            
        except NoSuchElementException:
            logging.info("No more pages available")
            return False
        except Exception as e:
            logging.warning(f"Error navigating to next page: {e}")
            return False

    # --------------- PDF Handling ---------------

    def _download_case_pdf(self, url: str, case_id: str) -> Optional[str]:
        """Download PDF file from URL."""
        pdf_name = f"{case_id}.pdf"
        pdf_path = os.path.join(self.pdf_dir, pdf_name)

        if os.path.exists(pdf_path):
            logging.debug(f"PDF already exists: {pdf_name}")
            return pdf_path

        try:
            # If URL is relative, make it absolute
            if not url.startswith('http'):
                url = urljoin(self.BASE_URL, url)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if we got a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                # Try to detect PDF by content
                if not response.content.startswith(b'%PDF'):
                    logging.warning(f"Response is not a PDF for URL: {url}")
                    return None

            with open(pdf_path, "wb") as fp:
                fp.write(response.content)
            
            logging.info(f"Downloaded: {pdf_name}")
            return pdf_path
            
        except Exception as e:
            logging.error(f"Error downloading PDF from {url}: {e}")
            return None

    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        if not pdf_path or not os.path.exists(pdf_path):
            return ""
        
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text_chunks.append(page.get_text())
            return "\n".join(text_chunks)
        except Exception as e:
            logging.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""

    # --------------- Utilities ---------------

    @staticmethod
    def _generate_case_id(case_no: str, case_year: str, idx: int) -> str:
        """Generate a unique case ID."""
        if case_no and case_year:
            # Clean case number
            clean_no = re.sub(r'[^\w\-]', '_', case_no)
            clean_no = re.sub(r'_+', '_', clean_no)  # Remove multiple underscores
            clean_no = clean_no.strip('_')
            return f"{clean_no}_{case_year}"
        return f"case_{idx}_{int(time.time())}"

    @staticmethod
    def _extract_ppc_sections(text: str) -> List[str]:
        """Extract PPC section references from judgment text."""
        if not text:
            return []
        
        patterns = [
            r"Section\s+(\d{1,3}[A-Z]?)\s+(?:of\s+)?(?:PPC|Pakistan Penal Code)",
            r"Section\s+(\d{1,3}[A-Z]?)\s+(?:of\s+)?P\.?P\.?C\.?",
            r"S\.\s*(\d{1,3}[A-Z]?)\s+PPC",
            r"(?:Section|Sec\.|S\.)\s+(\d{1,3}[A-Z]?)",
        ]
        
        sections = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            sections.update(matches)
        
        return sorted(sections)

    def _write_case_json(self, metadata: Dict):
        """Write case metadata to individual JSON file."""
        json_path = os.path.join(self.json_dir, f"{metadata['case_id']}.json")
        try:
            with open(json_path, "w", encoding="utf-8") as fp:
                json.dump(metadata, fp, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error writing JSON for {metadata['case_id']}: {e}")

    def _write_master_json(self, cases: List[Dict], filename: str):
        """Write master JSON file with all cases."""
        master_path = os.path.join(self.output_dir, filename)
        try:
            with open(master_path, "w", encoding="utf-8") as fp:
                json.dump(cases, fp, ensure_ascii=False, indent=2)
            logging.info(f"Master JSON written: {master_path}")
        except Exception as e:
            logging.error(f"Error writing master JSON: {e}")

    @staticmethod
    def _slugify(value: str) -> str:
        """Convert category names into filesystem-friendly strings."""
        value = value.lower().strip()
        value = re.sub(r"[\\s/]+", "_", value)
        value = re.sub(r"[^a-z0-9_\\-]", "", value)
        return value or "category"


if __name__ == "__main__":
    scraper = SHCCriminalScraper(
        output_dir="./data/raw/scraped/shc",
        headless=False,  # Set to False for debugging
        wait_timeout=30,
        throttle_sec=2.0
    )
    try:
        scraper.scrape_other_categories(
            skip_categories=["Cr.Appeal"],
            max_pages=None,  # scrape all pages
            combined_filename="shc_criminal_other_categories.json"
        )
    except Exception as e:
        logging.error(f"Scraper failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()