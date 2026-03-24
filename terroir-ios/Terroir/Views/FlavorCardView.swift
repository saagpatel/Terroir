import SwiftUI

struct FlavorCardView: View {
    let vector: FlavorVector
    let coordinate: GeoCoordinate
    let locationName: String
    let isOcean: Bool
    let oceanZone: Int
    let elevationBand: Int
    let onDismiss: () -> Void
    let onMoreDetail: () -> Void
    let onShare: () -> Void

    @State private var dragOffset: CGFloat = 0

    private var prose: String {
        TemplateEngine.describe(
            vector: vector,
            isOcean: isOcean,
            oceanZone: oceanZone,
            elevationBand: elevationBand
        )
    }

    var body: some View {
        VStack(spacing: 0) {
            // Drag handle
            Capsule()
                .fill(.white.opacity(0.4))
                .frame(width: 40, height: 4)
                .padding(.top, 10)
                .padding(.bottom, 8)

            ScrollView(.vertical, showsIndicators: false) {
                VStack(spacing: 20) {
                    // Location header
                    VStack(spacing: 4) {
                        Text(locationName)
                            .font(.system(size: 22, weight: .bold, design: .serif))
                            .foregroundStyle(.white)
                            .multilineTextAlignment(.center)

                        Text(coordinate.displayString)
                            .font(.system(size: 12, weight: .light, design: .monospaced))
                            .foregroundStyle(.white.opacity(0.6))
                    }

                    // Radar chart
                    RadarChartView(vector: vector)
                        .frame(width: 220, height: 220)

                    // Dominant note pills
                    dominantNotePills

                    // Prose description
                    Text(prose)
                        .font(.system(size: 14, weight: .light, design: .serif))
                        .foregroundStyle(.white.opacity(0.85))
                        .lineSpacing(6)
                        .multilineTextAlignment(.leading)
                        .padding(.horizontal, 8)

                    // Action buttons
                    HStack(spacing: 16) {
                        Button(action: onMoreDetail) {
                            Label("More Detail", systemImage: "text.magnifyingglass")
                                .font(.system(size: 13, weight: .medium))
                                .foregroundStyle(.white)
                                .padding(.horizontal, 16)
                                .padding(.vertical, 10)
                                .background(.white.opacity(0.12), in: Capsule())
                        }

                        Button(action: onShare) {
                            Label("Share", systemImage: "square.and.arrow.up")
                                .font(.system(size: 13, weight: .medium))
                                .foregroundStyle(.white)
                                .padding(.horizontal, 16)
                                .padding(.vertical, 10)
                                .background(.white.opacity(0.12), in: Capsule())
                        }
                    }
                    .padding(.bottom, 24)
                }
                .padding(.horizontal, 20)
            }
        }
        .frame(maxWidth: .infinity)
        .frame(maxHeight: UIScreen.main.bounds.height * 0.65)
        .background(
            RoundedRectangle(cornerRadius: 24)
                .fill(.ultraThinMaterial)
                .environment(\.colorScheme, .dark)
        )
        .clipShape(RoundedRectangle(cornerRadius: 24))
        .offset(y: dragOffset)
        .gesture(
            DragGesture()
                .onChanged { value in
                    if value.translation.height > 0 {
                        dragOffset = value.translation.height
                    }
                }
                .onEnded { value in
                    if value.translation.height > 120 {
                        withAnimation(.spring(response: 0.35, dampingFraction: 0.85)) {
                            dragOffset = UIScreen.main.bounds.height
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                            onDismiss()
                        }
                    } else {
                        withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                            dragOffset = 0
                        }
                    }
                }
        )
        .transition(.move(edge: .bottom).combined(with: .opacity))
    }

    @ViewBuilder
    private var dominantNotePills: some View {
        let notes = vector.dominantNotes()
        if !notes.isEmpty {
            FlowLayout(spacing: 8) {
                ForEach(notes, id: \.0) { dimension, intensity in
                    HStack(spacing: 4) {
                        Circle()
                            .fill(pillColor(for: intensity))
                            .frame(width: 6, height: 6)
                        Text(dimension.displayLabel)
                            .font(.system(size: 11, weight: .semibold, design: .serif))
                            .foregroundStyle(.white.opacity(0.9))
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(.white.opacity(0.1), in: Capsule())
                }
            }
        }
    }

    private func pillColor(for intensity: Float) -> Color {
        if intensity > 0.7 { return .orange }
        if intensity > 0.5 { return .yellow.opacity(0.8) }
        return .white.opacity(0.5)
    }
}

// MARK: - Flow Layout

struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache _: inout ()) -> CGSize {
        let rows = computeRows(proposal: proposal, subviews: subviews)
        let height = rows.reduce(CGFloat(0)) { total, row in
            total + row.height + (total > 0 ? spacing : 0)
        }
        return CGSize(width: proposal.width ?? 0, height: height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache _: inout ()) {
        let rows = computeRows(proposal: proposal, subviews: subviews)
        var y = bounds.minY

        for row in rows {
            let totalWidth = row.sizes.reduce(CGFloat(0)) { $0 + $1.width } + CGFloat(row.sizes.count - 1) * spacing
            var x = bounds.minX + (bounds.width - totalWidth) / 2

            for (index, size) in row.sizes.enumerated() {
                let subviewIndex = row.startIndex + index
                subviews[subviewIndex].place(
                    at: CGPoint(x: x, y: y),
                    proposal: ProposedViewSize(size)
                )
                x += size.width + spacing
            }
            y += row.height + spacing
        }
    }

    private struct Row {
        var startIndex: Int
        var sizes: [CGSize]
        var height: CGFloat
    }

    private func computeRows(proposal: ProposedViewSize, subviews: Subviews) -> [Row] {
        var rows: [Row] = []
        var currentRow = Row(startIndex: 0, sizes: [], height: 0)
        var x: CGFloat = 0
        let maxWidth = proposal.width ?? .infinity

        for (index, subview) in subviews.enumerated() {
            let size = subview.sizeThatFits(.unspecified)

            if x + size.width > maxWidth, !currentRow.sizes.isEmpty {
                rows.append(currentRow)
                currentRow = Row(startIndex: index, sizes: [], height: 0)
                x = 0
            }

            currentRow.sizes.append(size)
            currentRow.height = max(currentRow.height, size.height)
            x += size.width + spacing
        }

        if !currentRow.sizes.isEmpty {
            rows.append(currentRow)
        }

        return rows
    }
}
