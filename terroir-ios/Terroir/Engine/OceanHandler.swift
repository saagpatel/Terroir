import Foundation

enum OceanZone: Int, Sendable {
    case polar = 0
    case temperate = 1
    case tropical = 2

    static func from(latitude: Double) -> OceanZone {
        let absLat = abs(latitude)
        if absLat >= 60 { return .polar }
        if absLat >= 23.5 { return .temperate }
        return .tropical
    }

    var displayName: String {
        switch self {
        case .polar: "Polar Waters"
        case .temperate: "Temperate Sea"
        case .tropical: "Tropical Ocean"
        }
    }
}

enum OceanHandler {
    static func profile(for zone: OceanZone) -> FlavorVector {
        switch zone {
        case .polar:
            FlavorVector(
                earthy: 0, mineral: 0.9, bright: 0.6, citric: 0,
                floral: 0, herbaceous: 0, smoky: 0, woody: 0,
                saline: 0.7, tannic: 0, vegetal: 0, aromatic: 0
            )
        case .temperate:
            FlavorVector(
                earthy: 0, mineral: 0.7, bright: 0.5, citric: 0,
                floral: 0, herbaceous: 0, smoky: 0, woody: 0,
                saline: 0.8, tannic: 0, vegetal: 0, aromatic: 0
            )
        case .tropical:
            FlavorVector(
                earthy: 0, mineral: 0.4, bright: 0, citric: 0,
                floral: 0.3, herbaceous: 0, smoky: 0, woody: 0,
                saline: 0.9, tannic: 0, vegetal: 0, aromatic: 0
            )
        }
    }

    static func profile(forZoneIndex index: Int) -> FlavorVector {
        let zone = OceanZone(rawValue: index) ?? .temperate
        return profile(for: zone)
    }
}
