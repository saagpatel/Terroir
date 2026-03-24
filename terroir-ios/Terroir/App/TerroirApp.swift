import SwiftUI

@main
struct TerroirApp: App {
    @State private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(appState)
        }
    }
}

struct ContentView: View {
    @Environment(AppState.self) private var appState

    var body: some View {
        ZStack(alignment: .bottom) {
            // Globe fills the entire screen
            GlobeView(globeScene: appState.globeScene) { coordinate in
                Task {
                    await appState.handleGlobeTap(at: coordinate)
                }
            }
            .ignoresSafeArea()

            // Top-left overlay picker
            VStack {
                HStack {
                    overlayPicker
                    Spacer()
                    locationButton
                }
                .padding(.horizontal, 20)
                .padding(.top, 8)
                Spacer()
            }

            // Loading indicator
            if appState.isLoading {
                ProgressView()
                    .tint(.white)
                    .scaleEffect(1.2)
                    .frame(width: 60, height: 60)
                    .background(.ultraThinMaterial, in: Circle())
                    .environment(\.colorScheme, .dark)
            }

            // Flavor card overlay
            if appState.showingCard,
               let vector = appState.selectedVector,
               let coordinate = appState.selectedCoordinate
            {
                FlavorCardView(
                    vector: vector,
                    coordinate: coordinate,
                    locationName: appState.selectedLocationName,
                    isOcean: appState.selectedIsOcean,
                    oceanZone: appState.selectedOceanZone,
                    elevationBand: appState.selectedElevationBand,
                    onDismiss: {
                        appState.dismissCard()
                    },
                    onMoreDetail: {
                        Task { await appState.fetchEnrichment() }
                    },
                    onShare: {
                        appState.prepareShareCard()
                    }
                )
                .padding(.horizontal, 12)
                .padding(.bottom, 20)
            }
        }
        .task {
            await appState.loadFlavorGrid()
        }
        .alert("Error", isPresented: Binding(
            get: { appState.showingError },
            set: { appState.showingError = $0 }
        )) {
            Button("OK") { appState.showingError = false }
        } message: {
            Text(appState.errorMessage ?? "An unknown error occurred.")
        }
        .sheet(isPresented: Binding(
            get: { appState.showingDetail },
            set: { appState.showingDetail = $0 }
        )) {
            FlavorCardDetailView(
                enrichment: appState.enrichmentData ?? EnrichmentData(),
                locationName: appState.selectedLocationName
            )
        }
        .sheet(isPresented: Binding(
            get: { appState.showingShare },
            set: { appState.showingShare = $0 }
        )) {
            if let image = appState.shareImage {
                ShareSheet(items: [image])
            }
        }
        .preferredColorScheme(.dark)
    }

    // MARK: - Overlay Picker

    private var overlayPicker: some View {
        Menu {
            ForEach(GlobeOverlay.allCases) { overlay in
                Button {
                    appState.setOverlay(overlay)
                } label: {
                    Label(overlay.rawValue, systemImage: overlay.iconName)
                }
            }
        } label: {
            Image(systemName: appState.currentOverlay.iconName)
                .font(.system(size: 16, weight: .medium))
                .foregroundStyle(.white)
                .frame(width: 44, height: 44)
                .background(.ultraThinMaterial, in: Circle())
                .environment(\.colorScheme, .dark)
        }
    }

    // MARK: - Location Button

    private var locationButton: some View {
        Button {
            Task { await appState.goToMyLocation() }
        } label: {
            Image(systemName: "location.fill")
                .font(.system(size: 16, weight: .medium))
                .foregroundStyle(.white)
                .frame(width: 44, height: 44)
                .background(.ultraThinMaterial, in: Circle())
                .environment(\.colorScheme, .dark)
        }
    }
}

// MARK: - UIKit Share Sheet Bridge

struct ShareSheet: UIViewControllerRepresentable {
    let items: [Any]

    func makeUIViewController(context _: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }

    func updateUIViewController(_: UIActivityViewController, context _: Context) {}
}

#Preview {
    ContentView()
        .environment(AppState())
}
