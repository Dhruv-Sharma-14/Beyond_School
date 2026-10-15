import Foundation
import simd

public struct LugKinematicState: Sendable, Equatable {
    public var rotation: Float = 0
    public var outward: Float = 0
    public var isRemoved = false

    public init() {}
}

public struct MechanicalKinematicSnapshot: Sendable, Equatable {
    public var chassisLift: Float
    public var chassisRoll: Float
    public var chassisPitch: Float
    public var jackProgress: Float
    public var flatWheelPull: Float
    public var spareSwap: Float
    public var wakeRoll: Float
    public var cameraShake: Float
    public var lugs: [Int: LugKinematicState]

    public init(
        chassisLift: Float = 0,
        chassisRoll: Float = 0,
        chassisPitch: Float = 0,
        jackProgress: Float = 0,
        flatWheelPull: Float = 0,
        spareSwap: Float = 0,
        wakeRoll: Float = 0,
        cameraShake: Float = 0,
        lugs: [Int: LugKinematicState] = [:]
    ) {
        self.chassisLift = chassisLift
        self.chassisRoll = chassisRoll
        self.chassisPitch = chassisPitch
        self.jackProgress = jackProgress
        self.flatWheelPull = flatWheelPull
        self.spareSwap = spareSwap
        self.wakeRoll = wakeRoll
        self.cameraShake = cameraShake
        self.lugs = lugs
    }
}

@MainActor
public final class MechanicalKinematics {
    public private(set) var snapshot = MechanicalKinematicSnapshot()
    public let sagRoll: Float = 1.8 * .pi / 180
    public let sagPitch: Float = 1.8 * .pi / 180
    public let maximumLift: Float = 0.065
    public let wheelPullDistance: Float = 0.22
    public let spareSwapDistance: Float = 0.22
    public let lugStarOrder = [0, 2, 4, 1, 3]

    public init() {}

    public func setFlatTyreSag(_ enabled: Bool) {
        snapshot.chassisRoll = enabled ? sagRoll : 0
        snapshot.chassisPitch = enabled ? sagPitch : 0
    }

    public func setJackProgress(_ value: Float) {
        snapshot.jackProgress = value.clamped(to: 0...1)
        snapshot.chassisLift = smoothStep(snapshot.jackProgress) * maximumLift
    }

    public func setFlatWheelPull(_ value: Float) {
        snapshot.flatWheelPull = value.clamped(to: 0...1)
    }

    public func setSpareSwap(_ value: Float) {
        snapshot.spareSwap = value.clamped(to: 0...1)
    }

    public func injectWakeImpulse(direction: Float = 1) {
        snapshot.wakeRoll = direction * 0.35 * .pi / 180
        snapshot.cameraShake = 0.012
    }

    public func turnLug(_ index: Int, progress: Float, removed: Bool = false) {
        var lug = snapshot.lugs[index, default: LugKinematicState()]
        lug.rotation = smoothStep(progress) * 2 * .pi
        lug.outward = removed ? 0.035 : smoothStep(progress) * 0.004
        lug.isRemoved = removed
        snapshot.lugs[index] = lug
    }

    public func step(deltaTime: Float) {
        guard deltaTime > 0 else { return }
        snapshot.chassisLift = spring(snapshot.chassisLift, target: smoothStep(snapshot.jackProgress) * maximumLift, deltaTime: deltaTime)
        snapshot.chassisRoll = spring(snapshot.chassisRoll, target: snapshot.chassisLift > 0.001 ? 0 : sagRoll, deltaTime: deltaTime)
        snapshot.chassisPitch = spring(snapshot.chassisPitch, target: snapshot.chassisLift > 0.001 ? 0 : sagPitch, deltaTime: deltaTime)
        snapshot.wakeRoll = spring(snapshot.wakeRoll, target: 0, deltaTime: deltaTime)
        snapshot.cameraShake = spring(snapshot.cameraShake, target: 0, deltaTime: deltaTime)
    }

    private func spring(_ current: Float, target: Float, deltaTime: Float) -> Float {
        current + (target - current) * (1 - exp(-14 * deltaTime))
    }

    private func smoothStep(_ value: Float) -> Float {
        let t = value.clamped(to: 0...1)
        return t * t * (3 - 2 * t)
    }
}

private extension Comparable {
    func clamped(to range: ClosedRange<Self>) -> Self {
        min(max(self, range.lowerBound), range.upperBound)
    }
}
