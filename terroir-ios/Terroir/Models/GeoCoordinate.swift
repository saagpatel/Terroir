import Foundation

struct GeoCoordinate: Equatable, Hashable, Sendable {
    let latitude: Double
    let longitude: Double

    var gridCellIndex: Int {
        let latBand = Int(min(max((latitude + 90.0) / 0.5, 0), 359))
        let lonBand = Int(min(max((longitude + 180.0) / 0.5, 0), 719))
        return latBand * 720 + lonBand
    }

    var normalizedLongitude: Double {
        var lon = longitude
        while lon < -180 { lon += 360 }
        while lon > 180 { lon -= 360 }
        return lon
    }

    var latitudeString: String {
        let dir = latitude >= 0 ? "N" : "S"
        return String(format: "%.2f° %@", abs(latitude), dir)
    }

    var longitudeString: String {
        let dir = longitude >= 0 ? "E" : "W"
        return String(format: "%.2f° %@", abs(longitude), dir)
    }

    var displayString: String {
        "\(latitudeString), \(longitudeString)"
    }
}
