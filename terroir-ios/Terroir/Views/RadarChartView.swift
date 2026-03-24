import SwiftUI

struct RadarChartView: View {
    let vector: FlavorVector
    var accentColor: Color = .orange
    var gridColor: Color = .gray.opacity(0.3)

    private let dimensions = FlavorDimension.allCases
    private let ringLevels: [CGFloat] = [0.25, 0.5, 0.75, 1.0]

    var body: some View {
        GeometryReader { geometry in
            let center = CGPoint(x: geometry.size.width / 2, y: geometry.size.height / 2)
            let radius = min(geometry.size.width, geometry.size.height) / 2 - 32

            Canvas { context, _ in
                // Draw concentric rings
                for level in ringLevels {
                    let ringRadius = radius * level
                    let ringPath = Path(ellipseIn: CGRect(
                        x: center.x - ringRadius,
                        y: center.y - ringRadius,
                        width: ringRadius * 2,
                        height: ringRadius * 2
                    ))
                    context.stroke(ringPath, with: .color(gridColor), lineWidth: 0.5)
                }

                // Draw axis lines
                for dimension in dimensions {
                    let angle = dimension.radarAngle
                    let endPoint = pointOnCircle(center: center, radius: radius, angle: angle)
                    var axisPath = Path()
                    axisPath.move(to: center)
                    axisPath.addLine(to: endPoint)
                    context.stroke(axisPath, with: .color(gridColor), lineWidth: 0.5)
                }

                // Draw filled polygon
                let values = vector.asArray
                var polygonPath = Path()
                for (i, dimension) in dimensions.enumerated() {
                    let value = CGFloat(max(0, min(1, values[i])))
                    let angle = dimension.radarAngle
                    let point = pointOnCircle(center: center, radius: radius * value, angle: angle)
                    if i == 0 {
                        polygonPath.move(to: point)
                    } else {
                        polygonPath.addLine(to: point)
                    }
                }
                polygonPath.closeSubpath()

                context.fill(polygonPath, with: .color(accentColor.opacity(0.2)))
                context.stroke(polygonPath, with: .color(accentColor), lineWidth: 2)

                // Draw value dots
                for (i, dimension) in dimensions.enumerated() {
                    let value = CGFloat(max(0, min(1, values[i])))
                    let angle = dimension.radarAngle
                    let point = pointOnCircle(center: center, radius: radius * value, angle: angle)
                    let dotSize: CGFloat = value > 0.35 ? 5 : 3
                    let dotRect = CGRect(
                        x: point.x - dotSize / 2,
                        y: point.y - dotSize / 2,
                        width: dotSize,
                        height: dotSize
                    )
                    context.fill(Path(ellipseIn: dotRect), with: .color(accentColor))
                }
            }

            // Labels positioned outside the chart
            ForEach(Array(dimensions.enumerated()), id: \.element.id) { index, dimension in
                let angle = dimension.radarAngle
                let labelRadius = radius + 20
                let point = pointOnCircle(center: center, radius: labelRadius, angle: angle)

                Text(dimension.displayLabel)
                    .font(.system(size: 9, weight: .medium, design: .serif))
                    .foregroundStyle(.secondary)
                    .position(x: point.x, y: point.y)
                    .fixedSize()
            }
        }
    }

    private func pointOnCircle(center: CGPoint, radius: CGFloat, angle: Double) -> CGPoint {
        CGPoint(
            x: center.x + radius * CGFloat(cos(angle)),
            y: center.y + radius * CGFloat(sin(angle))
        )
    }
}

#Preview {
    RadarChartView(vector: .mockBurgundy)
        .frame(width: 280, height: 280)
        .padding()
        .background(.black)
        .preferredColorScheme(.dark)
}
