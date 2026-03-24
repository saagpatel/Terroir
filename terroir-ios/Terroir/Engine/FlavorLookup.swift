import Compression
import FlatBuffers
import Foundation

enum FlavorLookupError: Error, LocalizedError {
    case resourceNotFound
    case decompressionFailed
    case invalidData
    case indexOutOfBounds(Int)

    var errorDescription: String? {
        switch self {
        case .resourceNotFound:
            "terroir.bin not found in app bundle"
        case .decompressionFailed:
            "Failed to decompress LZ4 flavor grid data"
        case .invalidData:
            "Flavor grid data is invalid or corrupt"
        case .indexOutOfBounds(let index):
            "Grid cell index \(index) is out of bounds"
        }
    }
}

struct LookupResult: Sendable {
    let vector: FlavorVector
    let isOcean: Bool
    let oceanZone: Int
    let elevationBand: Int
}

actor FlavorLookup {
    private var grid: Terroir_FlavorGrid?
    private var buffer: ByteBuffer?
    private var isLoaded = false

    func load() throws {
        guard !isLoaded else { return }

        guard let url = Bundle.main.url(forResource: "terroir", withExtension: "bin") else {
            throw FlavorLookupError.resourceNotFound
        }

        let compressedData = try Data(contentsOf: url)

        guard compressedData.count >= 8 else {
            throw FlavorLookupError.invalidData
        }

        // Read 8-byte little-endian uint64 uncompressed size prefix.
        let uncompressedSize: UInt64 = compressedData.withUnsafeBytes { raw in
            raw.loadUnaligned(as: UInt64.self)
        }

        let payloadData = compressedData.dropFirst(8)
        let dstSize = Int(uncompressedSize)

        let decompressedBytes = UnsafeMutablePointer<UInt8>.allocate(capacity: dstSize)
        defer { decompressedBytes.deallocate() }

        let decodedSize: Int = payloadData.withUnsafeBytes { srcRaw in
            guard let srcBase = srcRaw.baseAddress else { return 0 }
            return compression_decode_buffer(
                decompressedBytes,
                dstSize,
                srcBase.assumingMemoryBound(to: UInt8.self),
                srcRaw.count,
                nil,
                COMPRESSION_LZ4_RAW
            )
        }

        guard decodedSize > 0 else {
            throw FlavorLookupError.decompressionFailed
        }

        let decompressedData = Data(bytes: decompressedBytes, count: decodedSize)
        let bb = ByteBuffer(data: decompressedData)
        let rootOffset = bb.read(def: Int32.self, position: bb.reader)
        let grid = Terroir_FlavorGrid(bb, o: rootOffset + Int32(bb.reader))

        self.buffer = bb
        self.grid = grid
        self.isLoaded = true
    }

    func lookup(coordinate: GeoCoordinate) throws -> LookupResult {
        guard let grid else {
            throw FlavorLookupError.invalidData
        }

        let index = coordinate.gridCellIndex

        guard index >= 0, index < Int(grid.latCells) * Int(grid.lonCells) else {
            throw FlavorLookupError.indexOutOfBounds(index)
        }
        let cell = grid.cells[index]

        let isOcean = cell.isOcean
        let oceanZone = Int(cell.oceanZone)
        let elevationBand = Int(cell.elevationBand)

        let vector: FlavorVector
        if isOcean {
            vector = OceanHandler.profile(forZoneIndex: oceanZone)
        } else {
            vector = FlavorVector(
                earthy: cell.earthy,
                mineral: cell.mineral,
                bright: cell.bright,
                citric: cell.citric,
                floral: cell.floral,
                herbaceous: cell.herbaceous,
                smoky: cell.smoky,
                woody: cell.woody,
                saline: cell.saline,
                tannic: cell.tannic,
                vegetal: cell.vegetal,
                aromatic: cell.aromatic
            )
        }

        return LookupResult(
            vector: vector,
            isOcean: isOcean,
            oceanZone: oceanZone,
            elevationBand: elevationBand
        )
    }
}
