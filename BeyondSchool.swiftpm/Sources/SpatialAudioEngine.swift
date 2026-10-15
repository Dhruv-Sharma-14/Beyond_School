import AVFoundation
import Foundation

#if canImport(RealityKit)
import RealityKit
#endif

@MainActor
public final class SpatialAudioEngine {
    public enum Cue: Sendable, Hashable {
        case flatTyreThump
        case wrenchCreak
        case jackClick
        case trafficWhoosh
    }

    public private(set) var lastCue: Cue?
    public private(set) var lastBufferFrameCount = 0
    public private(set) var attachedEntityNames: [Cue: String] = [:]
    public private(set) var generatedFileURLs: [Cue: URL] = [:]
    public private(set) var resourceLoadErrors: [String] = []

    #if canImport(RealityKit)
    private var resources: [Cue: AudioFileResource] = [:]
    private var attachedEntities: [Cue: Entity] = [:]
    private var playbackControllers: [Cue: AudioPlaybackController] = [:]
    #endif

    public init() {
        generateAndLoadResources()
    }

    public func trigger(_ cue: Cue, intensity: Float = 1) {
        lastCue = cue
        let buffer = makeBuffer(for: cue, intensity: intensity)
        lastBufferFrameCount = Int(buffer.frameLength)

        #if canImport(RealityKit)
        guard let resource = resources[cue],
              let entity = attachedEntities[cue] else { return }
        playbackControllers[cue]?.stop()
        playbackControllers[cue] = entity.playAudio(resource)
        #endif
    }

    public func attach(_ cue: Cue, toEntityNamed name: String) {
        attachedEntityNames[cue] = name
        trigger(cue, intensity: 0.01)
    }

    #if canImport(RealityKit)
    public func attach(_ cue: Cue, to entity: Entity, name: String? = nil) {
        attachedEntities[cue] = entity
        attachedEntityNames[cue] = name ?? entity.name
        entity.spatialAudio = SpatialAudioComponent(
            gain: .zero,
            directLevel: .zero,
            reverbLevel: .zero,
            directivity: .beam(focus: .zero)
        )
        if cue == .flatTyreThump || cue == .trafficWhoosh {
            trigger(cue, intensity: 0.01)
        }
    }

    public func stop(_ cue: Cue) {
        playbackControllers[cue]?.stop()
        playbackControllers[cue] = nil
    }
    #endif

    public func makeBuffer(
        for cue: Cue,
        intensity: Float = 1
    ) -> AVAudioPCMBuffer {
        let specification = specification(for: cue)
        return makeBuffer(
            frequency: specification.frequency,
            duration: specification.duration,
            intensity: intensity,
            waveform: specification.waveform
        )
    }

    public func makeBuffer(
        frequency: Double,
        duration: Double,
        intensity: Float
    ) -> AVAudioPCMBuffer {
        makeBuffer(
            frequency: frequency,
            duration: duration,
            intensity: intensity,
            waveform: .sine
        )
    }

    private func generateAndLoadResources() {
        for cue in Cue.allCases {
            let specification = specification(for: cue)
            let buffer = makeBuffer(
                frequency: specification.frequency,
                duration: specification.duration,
                intensity: 1,
                waveform: specification.waveform
            )
            let fileURL = FileManager.default.temporaryDirectory
                .appendingPathComponent(specification.fileName)
            do {
                try writeWAV(buffer: buffer, to: fileURL)
                generatedFileURLs[cue] = fileURL
                #if canImport(RealityKit)
                let configuration = AudioFileResource.Configuration(
                    loadingStrategy: .preload,
                    shouldLoop: specification.shouldLoop
                )
                resources[cue] = try AudioFileResource.load(
                    contentsOf: fileURL,
                    withName: specification.fileName,
                    configuration: configuration
                )
                #endif
            } catch {
                resourceLoadErrors.append("\(specification.fileName): \(error.localizedDescription)")
            }
        }
    }

    private func makeBuffer(
        frequency: Double,
        duration: Double,
        intensity: Float,
        waveform: Waveform
    ) -> AVAudioPCMBuffer {
        let sampleRate = 44_100.0
        let frames = AVAudioFrameCount(max(1, Int(sampleRate * duration)))
        let format = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 2)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: frames)!
        buffer.frameLength = frames
        let channels = buffer.floatChannelData!
        let clampedIntensity = intensity.clamped(to: 0...1)

        for frame in 0..<Int(frames) {
            let t = Double(frame) / sampleRate
            let normalizedTime = t / max(duration, 0.001)
            let envelope = waveform == .whoosh
                ? sin(.pi * normalizedTime).clamped(to: 0...1)
                : exp(-8 * normalizedTime)
            let carrier: Double
            switch waveform {
            case .sine, .whoosh:
                carrier = sin(2 * .pi * frequency * t)
            case .ratchet:
                carrier = sin(2 * .pi * frequency * t)
                    + 0.35 * sin(2 * .pi * frequency * 2.7 * t)
            }
            let sample = Float(carrier * envelope * Double(clampedIntensity))
            channels[0][frame] = sample
            channels[1][frame] = sample
        }
        return buffer
    }

    private func writeWAV(buffer: AVAudioPCMBuffer, to url: URL) throws {
        guard let channelData = buffer.floatChannelData else {
            throw AudioError.missingChannelData
        }
        let channelCount = Int(buffer.format.channelCount)
        let frameCount = Int(buffer.frameLength)
        let sampleRate = UInt32(buffer.format.sampleRate)
        let bitsPerSample: UInt16 = 16
        let blockAlign = UInt16(channelCount) * (bitsPerSample / 8)
        let byteRate = sampleRate * UInt32(blockAlign)
        let pcmByteCount = frameCount * channelCount * Int(bitsPerSample / 8)
        var data = Data(capacity: 44 + pcmByteCount)
        data.appendASCII("RIFF")
        data.appendLittleEndian(UInt32(36 + pcmByteCount))
        data.appendASCII("WAVE")
        data.appendASCII("fmt ")
        data.appendLittleEndian(UInt32(16))
        data.appendLittleEndian(UInt16(1))
        data.appendLittleEndian(UInt16(channelCount))
        data.appendLittleEndian(sampleRate)
        data.appendLittleEndian(byteRate)
        data.appendLittleEndian(blockAlign)
        data.appendLittleEndian(bitsPerSample)
        data.appendASCII("data")
        data.appendLittleEndian(UInt32(pcmByteCount))

        for frame in 0..<frameCount {
            for channel in 0..<channelCount {
                let sample = max(-1, min(1, channelData[channel][frame]))
                let pcm = Int16(sample * Float(Int16.max))
                data.appendLittleEndian(UInt16(bitPattern: pcm))
            }
        }
        try data.write(to: url, options: .atomic)
    }

    private func specification(for cue: Cue) -> CueSpecification {
        switch cue {
        case .flatTyreThump:
            return CueSpecification(
                frequency: 68,
                duration: 0.18,
                fileName: "thump.wav",
                shouldLoop: true,
                waveform: .sine
            )
        case .wrenchCreak:
            return CueSpecification(
                frequency: 420,
                duration: 0.12,
                fileName: "wrench_creak.wav",
                shouldLoop: false,
                waveform: .ratchet
            )
        case .jackClick:
            return CueSpecification(
                frequency: 1_100,
                duration: 0.045,
                fileName: "jack_click.wav",
                shouldLoop: false,
                waveform: .ratchet
            )
        case .trafficWhoosh:
            return CueSpecification(
                frequency: 180,
                duration: 0.70,
                fileName: "traffic_whoosh.wav",
                shouldLoop: true,
                waveform: .whoosh
            )
        }
    }

    private enum Waveform {
        case sine
        case ratchet
        case whoosh
    }

    private struct CueSpecification {
        let frequency: Double
        let duration: Double
        let fileName: String
        let shouldLoop: Bool
        let waveform: Waveform
    }

    private enum AudioError: LocalizedError {
        case missingChannelData

        var errorDescription: String? {
            "The synthesized PCM buffer has no channel data."
        }
    }
}

private extension Data {
    mutating func appendASCII(_ value: String) {
        append(value.data(using: .ascii)!)
    }

    mutating func appendLittleEndian<T: FixedWidthInteger>(_ value: T) {
        var littleEndian = value.littleEndian
        Swift.withUnsafeBytes(of: &littleEndian) { append(contentsOf: $0) }
    }
}

private extension Comparable {
    func clamped(to range: ClosedRange<Self>) -> Self {
        min(max(self, range.lowerBound), range.upperBound)
    }
}

private extension SpatialAudioEngine.Cue {
    static var allCases: [Self] {
        [.flatTyreThump, .wrenchCreak, .jackClick, .trafficWhoosh]
    }
}
