import Foundation

enum FlavorDimension: String, CaseIterable, Sendable, Identifiable {
    case earthy
    case mineral
    case bright
    case citric
    case floral
    case herbaceous
    case smoky
    case woody
    case saline
    case tannic
    case vegetal
    case aromatic

    var id: String { rawValue }

    var displayLabel: String {
        switch self {
        case .earthy: "Earthy"
        case .mineral: "Mineral"
        case .bright: "Bright"
        case .citric: "Citric"
        case .floral: "Floral"
        case .herbaceous: "Herbaceous"
        case .smoky: "Smoky"
        case .woody: "Woody"
        case .saline: "Saline"
        case .tannic: "Tannic"
        case .vegetal: "Vegetal"
        case .aromatic: "Aromatic"
        }
    }

    /// Angle in radians for positioning on the 12-axis radar chart, starting at top (12 o'clock).
    var radarAngle: Double {
        let index = Double(Self.allCases.firstIndex(of: self) ?? 0)
        return (index / 12.0) * 2.0 * .pi - .pi / 2.0
    }
}
