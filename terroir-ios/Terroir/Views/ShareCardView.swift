import SwiftUI

/// 1080x1080 composition designed for ImageRenderer export and social sharing.
struct ShareCardView: View {
    let vector: FlavorVector
    let coordinate: GeoCoordinate
    let locationName: String
    let isOcean: Bool
    let oceanZone: Int
    let elevationBand: Int

    private var prose: String {
        TemplateEngine.describe(
            vector: vector,
            isOcean: isOcean,
            oceanZone: oceanZone,
            elevationBand: elevationBand
        )
    }

    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                colors: [
                    Color(red: 0.08, green: 0.06, blue: 0.12),
                    Color(red: 0.14, green: 0.10, blue: 0.06),
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )

            VStack(spacing: 32) {
                // Header
                VStack(spacing: 6) {
                    Text("TERROIR")
                        .font(.system(size: 18, weight: .light, design: .serif))
                        .tracking(8)
                        .foregroundStyle(.white.opacity(0.5))

                    Text(locationName)
                        .font(.system(size: 36, weight: .bold, design: .serif))
                        .foregroundStyle(.white)
                        .multilineTextAlignment(.center)

                    Text(coordinate.displayString)
                        .font(.system(size: 14, weight: .light, design: .monospaced))
                        .foregroundStyle(.white.opacity(0.5))
                }

                // Radar chart
                RadarChartView(vector: vector, accentColor: .orange)
                    .frame(width: 380, height: 380)

                // Dominant notes
                let notes = vector.dominantNotes()
                if !notes.isEmpty {
                    HStack(spacing: 12) {
                        ForEach(notes.prefix(4), id: \.0) { dimension, _ in
                            Text(dimension.displayLabel.uppercased())
                                .font(.system(size: 12, weight: .bold, design: .serif))
                                .tracking(2)
                                .foregroundStyle(.orange.opacity(0.9))
                                .padding(.horizontal, 14)
                                .padding(.vertical, 6)
                                .background(.white.opacity(0.08), in: Capsule())
                        }
                    }
                }

                // Prose excerpt (first ~200 chars)
                Text(String(prose.prefix(200)) + (prose.count > 200 ? "..." : ""))
                    .font(.system(size: 16, weight: .light, design: .serif))
                    .foregroundStyle(.white.opacity(0.7))
                    .lineSpacing(5)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 48)
            }
            .padding(48)
        }
        .frame(width: 1080, height: 1080)
    }

    /// Renders the view to a UIImage for sharing.
    @MainActor
    func renderImage() -> UIImage? {
        let renderer = ImageRenderer(content: self)
        renderer.scale = 1.0
        return renderer.uiImage
    }
}

#Preview {
    ShareCardView(
        vector: .mockBurgundy,
        coordinate: GeoCoordinate(latitude: 47.23, longitude: 4.97),
        locationName: "Burgundy, France",
        isOcean: false,
        oceanZone: 0,
        elevationBand: 1
    )
    .scaleEffect(0.35)
}
