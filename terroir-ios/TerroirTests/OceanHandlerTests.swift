import Testing

@testable import Terroir

@Suite("OceanHandler")
struct OceanHandlerTests {

    @Test("Polar profile has mineral 0.9 and saline 0.7")
    func polarProfile() {
        let profile = OceanHandler.profile(for: .polar)
        #expect(profile.mineral == 0.9)
        #expect(profile.saline == 0.7)
        #expect(profile.bright == 0.6)
        #expect(profile.earthy == 0)
        #expect(profile.floral == 0)
    }

    @Test("Temperate profile has saline 0.8 and mineral 0.7")
    func temperateProfile() {
        let profile = OceanHandler.profile(for: .temperate)
        #expect(profile.saline == 0.8)
        #expect(profile.mineral == 0.7)
        #expect(profile.bright == 0.5)
        #expect(profile.earthy == 0)
    }

    @Test("Tropical profile has saline 0.9 and floral 0.3")
    func tropicalProfile() {
        let profile = OceanHandler.profile(for: .tropical)
        #expect(profile.saline == 0.9)
        #expect(profile.mineral == 0.4)
        #expect(profile.floral == 0.3)
        #expect(profile.earthy == 0)
    }

    @Test("forZoneIndex maps 0/1/2 to correct zones")
    func zoneIndexMapping() {
        let polar = OceanHandler.profile(forZoneIndex: 0)
        let temperate = OceanHandler.profile(forZoneIndex: 1)
        let tropical = OceanHandler.profile(forZoneIndex: 2)

        #expect(polar == OceanHandler.profile(for: .polar))
        #expect(temperate == OceanHandler.profile(for: .temperate))
        #expect(tropical == OceanHandler.profile(for: .tropical))
    }

    @Test("Invalid zone index defaults to temperate")
    func invalidZoneDefaultsToTemperate() {
        let profile = OceanHandler.profile(forZoneIndex: 99)
        #expect(profile == OceanHandler.profile(for: .temperate))
    }

    @Test("OceanZone.from latitude classifies correctly")
    func latitudeClassification() {
        #expect(OceanZone.from(latitude: 70) == .polar)
        #expect(OceanZone.from(latitude: -65) == .polar)
        #expect(OceanZone.from(latitude: 45) == .temperate)
        #expect(OceanZone.from(latitude: -30) == .temperate)
        #expect(OceanZone.from(latitude: 10) == .tropical)
        #expect(OceanZone.from(latitude: -5) == .tropical)
    }

    @Test("Boundary at 60° is polar")
    func boundaryAt60() {
        #expect(OceanZone.from(latitude: 60) == .polar)
        #expect(OceanZone.from(latitude: -60) == .polar)
    }

    @Test("Boundary at 23.5° is temperate")
    func boundaryAt23_5() {
        #expect(OceanZone.from(latitude: 23.5) == .temperate)
        #expect(OceanZone.from(latitude: -23.5) == .temperate)
    }

    @Test("Just below 23.5° is tropical")
    func justBelowTemperate() {
        #expect(OceanZone.from(latitude: 23.4) == .tropical)
    }

    @Test("All ocean profiles have zero earthy, woody, tannic, smoky, herbaceous, vegetal, aromatic, citric")
    func oceanProfilesHaveZeroLandDimensions() {
        for zone in [OceanZone.polar, .temperate, .tropical] {
            let profile = OceanHandler.profile(for: zone)
            #expect(profile.earthy == 0, "earthy should be 0 for \(zone)")
            #expect(profile.woody == 0, "woody should be 0 for \(zone)")
            #expect(profile.tannic == 0, "tannic should be 0 for \(zone)")
            #expect(profile.smoky == 0, "smoky should be 0 for \(zone)")
            #expect(profile.herbaceous == 0, "herbaceous should be 0 for \(zone)")
            #expect(profile.vegetal == 0, "vegetal should be 0 for \(zone)")
            #expect(profile.aromatic == 0, "aromatic should be 0 for \(zone)")
            #expect(profile.citric == 0, "citric should be 0 for \(zone)")
        }
    }

    @Test("Display names are human-readable")
    func displayNames() {
        #expect(OceanZone.polar.displayName == "Polar Waters")
        #expect(OceanZone.temperate.displayName == "Temperate Sea")
        #expect(OceanZone.tropical.displayName == "Tropical Ocean")
    }
}
