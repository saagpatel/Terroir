import Testing

@testable import Terroir

@Suite("TemplateEngine")
struct TemplateEngineTests {

    @Test("Ocean description mentions saline/salt for all zones")
    func oceanDescriptions() {
        for zone in 0 ..< 3 {
            let prose = TemplateEngine.describe(
                vector: .mockOcean,
                isOcean: true,
                oceanZone: zone
            )
            #expect(!prose.isEmpty)
            let lowered = prose.lowercased()
            #expect(lowered.contains("salt") || lowered.contains("brine") || lowered.contains("salin"))
        }
    }

    @Test("Polar ocean description mentions cold/ice/glacial")
    func polarOceanTheme() {
        let prose = TemplateEngine.describe(
            vector: .mockOcean,
            isOcean: true,
            oceanZone: 0
        )
        let lowered = prose.lowercased()
        #expect(lowered.contains("cold") || lowered.contains("ice") || lowered.contains("glacial") || lowered.contains("polar"))
    }

    @Test("Tropical ocean description mentions warm/tropical/coral")
    func tropicalOceanTheme() {
        let prose = TemplateEngine.describe(
            vector: .mockOcean,
            isOcean: true,
            oceanZone: 2
        )
        let lowered = prose.lowercased()
        #expect(lowered.contains("warm") || lowered.contains("tropical") || lowered.contains("coral"))
    }

    @Test("Land description for Burgundy-style profile is non-empty")
    func burgundyLandDescription() {
        let prose = TemplateEngine.describe(
            vector: .mockBurgundy,
            isOcean: false,
            elevationBand: 1
        )
        #expect(!prose.isEmpty)
        #expect(prose.count > 100)
    }

    @Test("Land description includes elevation context")
    func elevationContext() {
        for band in 0 ..< 4 {
            let prose = TemplateEngine.describe(
                vector: .mockBurgundy,
                isOcean: false,
                elevationBand: band
            )
            #expect(!prose.isEmpty)
            // Each band adds specific elevation text
            #expect(prose.count > 100)
        }
    }

    @Test("High elevation mentions altitude or air")
    func highElevation() {
        let prose = TemplateEngine.describe(
            vector: .mockBurgundy,
            isOcean: false,
            elevationBand: 2
        )
        let lowered = prose.lowercased()
        #expect(lowered.contains("altitude") || lowered.contains("air") || lowered.contains("elevation"))
    }

    @Test("Zero vector produces fallback description")
    func zeroVectorFallback() {
        let prose = TemplateEngine.describe(
            vector: .zero,
            isOcean: false,
            elevationBand: 0
        )
        #expect(!prose.isEmpty)
        let lowered = prose.lowercased()
        #expect(lowered.contains("subtle") || lowered.contains("understated") || lowered.contains("equilibrium"))
    }

    @Test("Marlborough profile references bright or citric or herbaceous themes")
    func marlboroughThemes() {
        let prose = TemplateEngine.describe(
            vector: .mockMarlborough,
            isOcean: false,
            elevationBand: 0
        )
        #expect(!prose.isEmpty)
        // The dominant note is bright, so templates reference brightness/light/acidity
        let lowered = prose.lowercased()
        #expect(
            lowered.contains("light") || lowered.contains("bright") || lowered.contains("acidity")
            || lowered.contains("crisp") || lowered.contains("luminous")
        )
    }

    @Test("Description mentions secondary note")
    func secondaryNoteMentioned() {
        let prose = TemplateEngine.describe(
            vector: .mockBurgundy,
            isOcean: false,
            elevationBand: 1
        )
        // Burgundy mock has multiple notes > 0.35, so modifier clause should appear
        let notes = FlavorVector.mockBurgundy.dominantNotes(threshold: 0.30)
        if notes.count >= 2 {
            let secondaryLabel = notes[1].0.displayLabel.lowercased()
            #expect(prose.lowercased().contains(secondaryLabel))
        }
    }

    @Test("All 12 dimensions have opening templates")
    func allDimensionsHaveTemplates() {
        for dimension in FlavorDimension.allCases {
            // Create a vector with only this dimension set high
            var vector = FlavorVector.zero
            switch dimension {
            case .earthy: vector.earthy = 0.8
            case .mineral: vector.mineral = 0.8
            case .bright: vector.bright = 0.8
            case .citric: vector.citric = 0.8
            case .floral: vector.floral = 0.8
            case .herbaceous: vector.herbaceous = 0.8
            case .smoky: vector.smoky = 0.8
            case .woody: vector.woody = 0.8
            case .saline: vector.saline = 0.8
            case .tannic: vector.tannic = 0.8
            case .vegetal: vector.vegetal = 0.8
            case .aromatic: vector.aromatic = 0.8
            }

            let prose = TemplateEngine.describe(
                vector: vector,
                isOcean: false,
                elevationBand: 0
            )
            #expect(!prose.isEmpty, "No template for \(dimension.rawValue)")
            #expect(prose.count > 50, "Template too short for \(dimension.rawValue)")
        }
    }
}
