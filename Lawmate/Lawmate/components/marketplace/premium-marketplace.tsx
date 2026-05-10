"use client"

import { useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, SlidersHorizontal, X, MapPin, Star, DollarSign, Award, TrendingUp } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { LawyerCardPremium, type LawyerData } from "./lawyer-card-premium"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useLanguage } from "@/lib/language"

interface PremiumMarketplaceProps {
  lawyers: LawyerData[]
  onConnect?: (lawyerId: string) => void
  onViewProfile?: (lawyerId: string) => void
}

export function PremiumMarketplace({ lawyers, onConnect, onViewProfile }: PremiumMarketplaceProps) {
  const { t } = useLanguage()
  const [searchQuery, setSearchQuery] = useState("")
  const [showFilters, setShowFilters] = useState(false)
  const [selectedSpecializations, setSelectedSpecializations] = useState<string[]>([])
  const [selectedLocation, setSelectedLocation] = useState<string>("")
  const [priceRange, setPriceRange] = useState([0, 1000])
  const [minRating, setMinRating] = useState(0)
  const [sortBy, setSortBy] = useState("rating")
  const [onlyAvailable, setOnlyAvailable] = useState(false)

  // Extract unique values for filters
  const allSpecializations = useMemo(() => {
    const specs = new Set<string>()
    lawyers.forEach(lawyer => lawyer.specialization.forEach(spec => specs.add(spec)))
    return Array.from(specs).sort()
  }, [lawyers])

  const allLocations = useMemo(() => {
    return Array.from(new Set(lawyers.map(l => l.location))).sort()
  }, [lawyers])

  // Filtered and sorted lawyers
  const filteredLawyers = useMemo(() => {
    let filtered = lawyers.filter(lawyer => {
      const matchesSearch = lawyer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        lawyer.specialization.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()))

      const matchesSpecialization = selectedSpecializations.length === 0 ||
        selectedSpecializations.some(spec => lawyer.specialization.includes(spec))

      const matchesLocation = !selectedLocation || lawyer.location === selectedLocation

      const matchesPrice = lawyer.hourlyRate >= priceRange[0] && lawyer.hourlyRate <= priceRange[1]

      const matchesRating = lawyer.rating >= minRating

      const matchesAvailability = !onlyAvailable || lawyer.available

      return matchesSearch && matchesSpecialization && matchesLocation &&
        matchesPrice && matchesRating && matchesAvailability
    })

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "rating":
          return b.rating - a.rating
        case "price-low":
          return a.hourlyRate - b.hourlyRate
        case "price-high":
          return b.hourlyRate - a.hourlyRate
        case "experience":
          return b.experience - a.experience
        case "success":
          return b.successRate - a.successRate
        default:
          return 0
      }
    })

    return filtered
  }, [lawyers, searchQuery, selectedSpecializations, selectedLocation, priceRange, minRating, sortBy, onlyAvailable])

  const toggleSpecialization = (spec: string) => {
    setSelectedSpecializations(prev =>
      prev.includes(spec) ? prev.filter(s => s !== spec) : [...prev, spec]
    )
  }

  const clearAllFilters = () => {
    setSearchQuery("")
    setSelectedSpecializations([])
    setSelectedLocation("")
    setPriceRange([0, 1000])
    setMinRating(0)
    setOnlyAvailable(false)
  }

  const activeFiltersCount = [
    searchQuery,
    ...selectedSpecializations,
    selectedLocation,
    minRating > 0,
    onlyAvailable,
  ].filter(Boolean).length

  return (
    <div className="space-y-6">
      {/* Header with Search and Filter Toggle */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search Bar */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder={t("lawyers.search_ph")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-background/50 border-border/50 focus:border-primary/50"
          />
        </div>

        {/* Filter Toggle & Sort */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="gap-2 relative"
          >
            <SlidersHorizontal className="w-4 h-4" />
            {t("lawyers.filters")}
            {activeFiltersCount > 0 && (
              <Badge className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs bg-primary">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="rating">{t("lawyers.highest_rated")}</SelectItem>
              <SelectItem value="price-low">Price: Low to High</SelectItem>
              <SelectItem value="price-high">Price: High to Low</SelectItem>
              <SelectItem value="experience">Most Experienced</SelectItem>
              <SelectItem value="success">Success Rate</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Advanced Filters Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-6 rounded-xl border border-border bg-card/50 backdrop-blur-sm space-y-6">
              {/* Quick Filters Row */}
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-foreground">Advanced Filters</h3>
                {activeFiltersCount > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearAllFilters}
                    className="gap-2 text-muted-foreground hover:text-foreground"
                  >
                    <X className="w-4 h-4" />
                    Clear All
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Specialization Filter */}
                <div className="space-y-3">
                  <label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <Award className="w-4 h-4" />
                    Specialization
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {allSpecializations.slice(0, 6).map((spec) => (
                      <Badge
                        key={spec}
                        variant={selectedSpecializations.includes(spec) ? "default" : "outline"}
                        className="cursor-pointer hover:bg-primary/20 transition-colors"
                        onClick={() => toggleSpecialization(spec)}
                      >
                        {spec}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Location Filter */}
                <div className="space-y-3">
                  <label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    Location
                  </label>
                  <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                    <SelectTrigger>
                      <SelectValue placeholder="All locations" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All locations</SelectItem>
                      {allLocations.map((location) => (
                        <SelectItem key={location} value={location}>
                          {location}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Price Range Filter */}
                <div className="space-y-3">
                  <label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    Hourly Rate: ${priceRange[0]} - ${priceRange[1]}
                  </label>
                  <Slider
                    min={0}
                    max={1000}
                    step={50}
                    value={priceRange}
                    onValueChange={setPriceRange}
                    className="mt-2"
                  />
                </div>

                {/* Rating Filter */}
                <div className="space-y-3">
                  <label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <Star className="w-4 h-4" />
                    Minimum Rating: {minRating > 0 ? `${minRating}+` : "Any"}
                  </label>
                  <div className="flex gap-2">
                    {[0, 3, 4, 4.5].map((rating) => (
                      <Button
                        key={rating}
                        size="sm"
                        variant={minRating === rating ? "default" : "outline"}
                        onClick={() => setMinRating(rating)}
                        className="flex-1"
                      >
                        {rating === 0 ? "Any" : `${rating}+`}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Availability Toggle */}
              <div className="flex items-center gap-3 pt-4 border-t border-border/50">
                <Button
                  variant={onlyAvailable ? "default" : "outline"}
                  size="sm"
                  onClick={() => setOnlyAvailable(!onlyAvailable)}
                  className="gap-2"
                >
                  <TrendingUp className="w-4 h-4" />
                  {onlyAvailable ? "Showing Available Only" : "Show Available Only"}
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results Count */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          {t("lawyers.showing")} <span className="font-semibold text-foreground">{filteredLawyers.length}</span> {t("lawyers.of")}{" "}
          <span className="font-semibold text-foreground">{lawyers.length}</span> {t("lawyers.title").toLowerCase()}
        </span>
        {activeFiltersCount > 0 && (
          <span className="text-primary font-medium">{activeFiltersCount} filter(s) active</span>
        )}
      </div>

      {/* Lawyers Grid */}
      <motion.div
        layout
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        <AnimatePresence mode="popLayout">
          {filteredLawyers.map((lawyer, index) => (
            <LawyerCardPremium
              key={lawyer.id}
              lawyer={lawyer}
              delay={index * 0.05}
              onConnect={() => onConnect?.(lawyer.id)}
              onViewProfile={() => onViewProfile?.(lawyer.id)}
            />
          ))}
        </AnimatePresence>
      </motion.div>

      {/* Empty State */}
      {filteredLawyers.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <div className="w-20 h-20 rounded-full bg-muted/50 flex items-center justify-center mx-auto mb-4">
            <Search className="w-10 h-10 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">No lawyers found</h3>
          <p className="text-muted-foreground mb-4">Try adjusting your filters or search query</p>
          {activeFiltersCount > 0 && (
            <Button onClick={clearAllFilters} variant="outline">
              Clear All Filters
            </Button>
          )}
        </motion.div>
      )}
    </div>
  )
}
