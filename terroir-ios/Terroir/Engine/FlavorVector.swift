import Foundation

struct FlavorVector: Sendable, Equatable {
    var earthy: Float
    var mineral: Float
    var bright: Float
    var citric: Float
    var floral: Float
    var herbaceous: Float
    var smoky: Float
    var woody: Float
    var saline: Float
    var tannic: Float
    var vegetal: Float
    var aromatic: Float

    var asArray: [Float] {
        [earthy, mineral, bright, citric, floral, herbaceous,
         smoky, woody, saline, tannic, vegetal, aromatic]
    }

    /// Returns dimensions with intensity above the threshold, sorted descending, capped at count.
    func dominantNotes(threshold: Float = 0.35, maxCount: Int = 5) -> [(FlavorDimension, Float)] {
        let pairs: [(FlavorDimension, Float)] = zip(FlavorDimension.allCases, asArray)
            .filter { $0.1 > threshold }
            .sorted { $0.1 > $1.1 }
        return Array(pairs.prefix(maxCount))
    }

    /// Value for a given dimension.
    func value(for dimension: FlavorDimension) -> Float {
        switch dimension {
        case .earthy: earthy
        case .mineral: mineral
        case .bright: bright
        case .citric: citric
        case .floral: floral
        case .herbaceous: herbaceous
        case .smoky: smoky
        case .woody: woody
        case .saline: saline
        case .tannic: tannic
        case .vegetal: vegetal
        case .aromatic: aromatic
        }
    }

    static let zero = FlavorVector(
        earthy: 0, mineral: 0, bright: 0, citric: 0, floral: 0, herbaceous: 0,
        smoky: 0, woody: 0, saline: 0, tannic: 0, vegetal: 0, aromatic: 0
    )

    // MARK: - Mock Data

    /// Burgundy-style: earthy, mineral, tannic, woody, aromatic.
    static let mockBurgundy = FlavorVector(
        earthy: 0.82, mineral: 0.71, bright: 0.25, citric: 0.15, floral: 0.38,
        herbaceous: 0.20, smoky: 0.45, woody: 0.68, saline: 0.10, tannic: 0.75,
        vegetal: 0.18, aromatic: 0.62
    )

    /// Marlborough-style: bright, citric, herbaceous, floral.
    static let mockMarlborough = FlavorVector(
        earthy: 0.15, mineral: 0.30, bright: 0.88, citric: 0.82, floral: 0.55,
        herbaceous: 0.78, smoky: 0.05, woody: 0.10, saline: 0.25, tannic: 0.12,
        vegetal: 0.45, aromatic: 0.60
    )

    /// Ocean/maritime profile: saline, mineral dominant.
    static let mockOcean = FlavorVector(
        earthy: 0.0, mineral: 0.70, bright: 0.50, citric: 0.0, floral: 0.0,
        herbaceous: 0.0, smoky: 0.0, woody: 0.0, saline: 0.80, tannic: 0.0,
        vegetal: 0.0, aromatic: 0.0
    )
}
