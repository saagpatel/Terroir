import Testing

@testable import Terroir

@Suite("GeoCoordinate")
struct GeoCoordinateTests {

    @Test("Grid cell index at origin (0°, 0°)")
    func gridIndexAtOrigin() {
        let coord = GeoCoordinate(latitude: 0, longitude: 0)
        // latBand = (0+90)/0.5 = 180, lonBand = (0+180)/0.5 = 360
        #expect(coord.gridCellIndex == 180 * 720 + 360)
    }

    @Test("Grid cell index at south-west corner (-90°, -180°)")
    func gridIndexAtSouthWest() {
        let coord = GeoCoordinate(latitude: -90, longitude: -180)
        // latBand = 0, lonBand = 0
        #expect(coord.gridCellIndex == 0)
    }

    @Test("Grid cell index at north-east corner (89.75°, 179.75°)")
    func gridIndexAtNorthEast() {
        let coord = GeoCoordinate(latitude: 89.75, longitude: 179.75)
        // latBand = (89.75+90)/0.5 = 359, lonBand = (179.75+180)/0.5 = 719
        #expect(coord.gridCellIndex == 359 * 720 + 719)
    }

    @Test("Grid cell index clamps latitude above 90°")
    func gridIndexClampsHighLatitude() {
        let coord = GeoCoordinate(latitude: 100, longitude: 0)
        // (100+90)/0.5 = 380, clamped to 359
        let expected = 359 * 720 + 360
        #expect(coord.gridCellIndex == expected)
    }

    @Test("Grid cell index clamps longitude below -180°")
    func gridIndexClampsLowLongitude() {
        let coord = GeoCoordinate(latitude: 0, longitude: -200)
        // (-200+180)/0.5 = -40, clamped to 0
        let expected = 180 * 720 + 0
        #expect(coord.gridCellIndex == expected)
    }

    @Test("Burgundy coordinate produces expected grid index")
    func burgundyIndex() {
        let coord = GeoCoordinate(latitude: 47.2, longitude: 5.0)
        let latBand = Int((47.2 + 90.0) / 0.5) // 274
        let lonBand = Int((5.0 + 180.0) / 0.5)  // 370
        #expect(coord.gridCellIndex == latBand * 720 + lonBand)
    }

    @Test("Display string formats correctly")
    func displayString() {
        let coord = GeoCoordinate(latitude: 47.23, longitude: -122.33)
        #expect(coord.latitudeString.contains("N"))
        #expect(coord.longitudeString.contains("W"))
        #expect(coord.displayString.contains(","))
    }

    @Test("Southern hemisphere shows S direction")
    func southernHemisphere() {
        let coord = GeoCoordinate(latitude: -34.6, longitude: 138.9)
        #expect(coord.latitudeString.contains("S"))
        #expect(coord.longitudeString.contains("E"))
    }

    @Test("GeoCoordinate conforms to Equatable")
    func equatable() {
        let a = GeoCoordinate(latitude: 10, longitude: 20)
        let b = GeoCoordinate(latitude: 10, longitude: 20)
        let c = GeoCoordinate(latitude: 10, longitude: 21)
        #expect(a == b)
        #expect(a != c)
    }

    @Test("GeoCoordinate conforms to Hashable")
    func hashable() {
        let a = GeoCoordinate(latitude: 10, longitude: 20)
        let b = GeoCoordinate(latitude: 10, longitude: 20)
        #expect(a.hashValue == b.hashValue)
    }

    @Test("Total grid cells is 259,200")
    func totalGridCells() {
        // 360 lat bands * 720 lon bands
        #expect(360 * 720 == 259_200)

        // Verify max index is within bounds
        let maxCoord = GeoCoordinate(latitude: 89.75, longitude: 179.75)
        #expect(maxCoord.gridCellIndex < 259_200)
    }
}
