import Testing

@testable import Terroir

@Suite("FlavorLookup")
struct FlavorLookupTests {

    @Test("FlavorVector asArray returns 12 elements")
    func vectorArrayLength() {
        let v = FlavorVector.mockBurgundy
        #expect(v.asArray.count == 12)
    }

    @Test("FlavorVector dominant notes filters by threshold")
    func dominantNotesThreshold() {
        let v = FlavorVector.mockBurgundy
        let notes = v.dominantNotes(threshold: 0.35)
        for (_, intensity) in notes {
            #expect(intensity > 0.35)
        }
    }

    @Test("FlavorVector dominant notes are sorted descending")
    func dominantNotesSorted() {
        let v = FlavorVector.mockBurgundy
        let notes = v.dominantNotes()
        for i in 1 ..< notes.count {
            #expect(notes[i - 1].1 >= notes[i].1)
        }
    }

    @Test("FlavorVector dominant notes capped at maxCount")
    func dominantNotesCapped() {
        let v = FlavorVector.mockBurgundy
        let notes = v.dominantNotes(threshold: 0.0, maxCount: 3)
        #expect(notes.count <= 3)
    }

    @Test("FlavorVector.zero has all zeros")
    func zeroVector() {
        let v = FlavorVector.zero
        for value in v.asArray {
            #expect(value == 0)
        }
    }

    @Test("FlavorVector value(for:) returns correct dimension")
    func valueForDimension() {
        let v = FlavorVector.mockBurgundy
        #expect(v.value(for: .earthy) == v.earthy)
        #expect(v.value(for: .mineral) == v.mineral)
        #expect(v.value(for: .saline) == v.saline)
        #expect(v.value(for: .aromatic) == v.aromatic)
    }

    @Test("FlavorVector mockOcean has saline and mineral as dominant")
    func mockOceanDominant() {
        let notes = FlavorVector.mockOcean.dominantNotes(threshold: 0.35)
        let dimensions = notes.map(\.0)
        #expect(dimensions.contains(.saline))
        #expect(dimensions.contains(.mineral))
    }

    @Test("FlavorVector mockMarlborough has bright as top note")
    func mockMarlboroughTop() {
        let notes = FlavorVector.mockMarlborough.dominantNotes()
        #expect(notes.first?.0 == .bright)
    }

    @Test("FlavorVector dominant notes returns empty for zero vector")
    func zeroVectorNoDominant() {
        let notes = FlavorVector.zero.dominantNotes()
        #expect(notes.isEmpty)
    }

    @Test("LookupResult stores all fields correctly")
    func lookupResultFields() {
        let result = LookupResult(
            vector: .mockBurgundy,
            isOcean: false,
            oceanZone: 0,
            elevationBand: 2
        )
        #expect(result.isOcean == false)
        #expect(result.oceanZone == 0)
        #expect(result.elevationBand == 2)
        #expect(result.vector == .mockBurgundy)
    }
}
