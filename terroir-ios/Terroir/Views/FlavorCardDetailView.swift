import SwiftUI

struct FlavorCardDetailView: View {
    let enrichment: EnrichmentData
    let locationName: String

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 28) {
                    if let soil = enrichment.soilDescription {
                        detailSection(
                            icon: "mountain.2",
                            title: "Soil",
                            body: soil
                        )
                    }

                    if let climate = enrichment.climateDescription {
                        detailSection(
                            icon: "cloud.sun",
                            title: "Climate",
                            body: climate
                        )
                    }

                    if let vegetation = enrichment.vegetationDescription {
                        detailSection(
                            icon: "leaf",
                            title: "Vegetation",
                            body: vegetation
                        )
                    }

                    if let geology = enrichment.geologicalHistory {
                        detailSection(
                            icon: "fossil.shell",
                            title: "Geological History",
                            body: geology
                        )
                    }

                    if let appellations = enrichment.nearbyAppellations {
                        detailSection(
                            icon: "mappin.and.ellipse",
                            title: "Nearby Appellations",
                            body: appellations
                        )
                    }

                    if let culture = enrichment.culturalContext {
                        detailSection(
                            icon: "books.vertical",
                            title: "Cultural Context",
                            body: culture
                        )
                    }

                    if !enrichment.hasContent {
                        ContentUnavailableView(
                            "No Enrichment Data",
                            systemImage: "globe.desk",
                            description: Text(
                                "Detailed terroir information is not yet available for this location. "
                                + "Check back after the next data update."
                            )
                        )
                    }
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 16)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle(locationName)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                        .fontWeight(.semibold)
                }
            }
        }
    }

    @ViewBuilder
    private func detailSection(icon: String, title: String, body: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(title, systemImage: icon)
                .font(.system(size: 15, weight: .bold, design: .serif))
                .foregroundStyle(.primary)

            Text(body)
                .font(.system(size: 14, weight: .light, design: .serif))
                .foregroundStyle(.secondary)
                .lineSpacing(5)
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))
    }
}

#Preview {
    FlavorCardDetailView(
        enrichment: EnrichmentData(
            soilDescription: "Deep alluvial clay with limestone bedrock at 2m depth.",
            climateDescription: "Continental with warm summers and cold, dry winters.",
            vegetationDescription: "Dense vineyard cover with scattered oak woodlands.",
            geologicalHistory: "Jurassic limestone formed 150 million years ago.",
            nearbyAppellations: "Gevrey-Chambertin, Morey-Saint-Denis",
            culturalContext: "The Cistercian monks first mapped these vineyards in the 12th century."
        ),
        locationName: "Burgundy, France"
    )
}
