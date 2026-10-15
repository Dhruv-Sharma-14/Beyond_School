import Foundation
import Observation

@MainActor
@Observable
public final class RoadsideTrainerModel {
    public enum ProcedureMode: String, CaseIterable, Sendable {
        case manual = "Manual"
        case assisted = "Assisted"
    }

    public enum State: String, CaseIterable, Sendable {
        case drivingIntro
        case tyreWarningPullOver
        case secureCockpit
        case mirrorCheckAndExit
        case inspectFlatAndCall1033
        case trunkToolkitHandOff
        case assistedWheelChange
        case recallChallenge
    }

    public enum Action: Sendable {
        case startExperience
        case observeHighway
        case steerToShoulder
        case brakeToStop
        case selectProcedure(ProcedureMode)
        case shiftToPark
        case engageParkingBrake
        case pressHazards
        case checkDriverMirror
        case openDriverDoor
        case inspectFlatTyre
        case call1033
        case dial1033
        case placeWarningTriangle
        case openTrunk
        case grabToolkit(Tool)
        case crackLug(Int)
        case positionJack
        case crankJack
        case removeWheel
        case mountSpare
        case torqueLug(Int)
        case lowerJack
        case beginRecall
        case requestHint
        case replayPractice
    }

    public enum Tool: String, CaseIterable, Sendable {
        case lugWrench = "Lug wrench"
        case scissorJack = "Scissor jack"
        case spareWheel = "Spare wheel"
    }

    public private(set) var state: State = .drivingIntro
    public private(set) var procedureMode: ProcedureMode?
    public private(set) var feedback = "Observe the road, mirror, and HIGHWAY ASSISTANCE sign."
    public private(set) var hazardLampsActive = false
    public private(set) var driverDoorOpen = false
    public private(set) var trunkOpen = false
    public private(set) var jackPositioned = false
    public private(set) var jackRaised = false
    public private(set) var flatWheelRemoved = false
    public private(set) var spareMounted = false
    public private(set) var recallHintsUsed = 0
    public private(set) var trafficDangerZoneOccupied = false
    public private(set) var crackedLugs: [Int] = []
    public private(set) var torquedLugs: [Int] = []
    public private(set) var grabbedTools: Set<Tool> = []
    public private(set) var recallStep = 0
    public private(set) var dialerConnected = false
    public private(set) var experienceStarted = false
    public private(set) var experienceCompleted = false
    public private(set) var totalElapsedSeconds = 0
    public private(set) var safetyChecksPassed = 0
    private var experienceStartDate: Date?

    public static let starPattern = [0, 2, 4, 1, 3]

    public init() {}

    @discardableResult
    public func send(_ action: Action) -> Bool {
        if experienceCompleted, case .replayPractice = action {
            resetExperience()
            return true
        }
        if state == .recallChallenge, !isRecallControl(action) {
            return handleRecall(action)
        }
        switch (state, action) {
        case (.drivingIntro, .startExperience):
            experienceStarted = true
            experienceStartDate = Date()
            feedback = "Experience started. Observe the road, mirror, and HIGHWAY ASSISTANCE sign."
        case (.drivingIntro, .observeHighway):
            advance(to: .tyreWarningPullOver, feedback: "A thump and cluster alert appear. Steer smoothly toward the shoulder.")
        case (.tyreWarningPullOver, .steerToShoulder):
            feedback = "Good lane control. Brake progressively inside the marked shoulder zone."
        case (.tyreWarningPullOver, .brakeToStop):
            advance(to: .secureCockpit, feedback: "Select a procedure, then secure the vehicle before exiting.")
        case (.secureCockpit, .selectProcedure(let mode)):
            procedureMode = mode
            feedback = "Shift to Park, engage the parking brake, and press the hazard switch."
        case (.secureCockpit, .shiftToPark):
            feedback = "Transmission is in Park. Engage the parking brake."
        case (.secureCockpit, .engageParkingBrake):
            feedback = "Parking brake engaged. Press the hazard switch."
        case (.secureCockpit, .pressHazards):
            hazardLampsActive = true
            advance(to: .mirrorCheckAndExit, feedback: "Hazards are active. Check the driver mirror for passing traffic.")
        case (.mirrorCheckAndExit, .checkDriverMirror):
            feedback = "Mirror checked. Open the driver door only when the traffic gap is safe."
        case (.mirrorCheckAndExit, .openDriverDoor):
            guard !trafficDangerZoneOccupied else {
                return coach("A passing vehicle is too close. Check MIRROR_Driver and wait for a safe gap before opening the door.")
            }
            driverDoorOpen = true
            advance(to: .inspectFlatAndCall1033, feedback: "Inspect the rear-left tyre, call 1033, and place the warning triangle.")
        case (.inspectFlatAndCall1033, .inspectFlatTyre):
            feedback = "The rear-left carcass is visibly deflated. Call National Highway Assistance 1033."
        case (.inspectFlatAndCall1033, .call1033):
            feedback = "1033 connected. Place the warning triangle well behind the vehicle."
            dialerConnected = true
            safetyChecksPassed += 1
        case (.inspectFlatAndCall1033, .dial1033):
            dialerConnected = true
            feedback = "1033 connected. Place the warning triangle well behind the vehicle."
        case (.inspectFlatAndCall1033, .placeWarningTriangle):
            advance(to: .trunkToolkitHandOff, feedback: "Open the trunk and identify the lug wrench, jack, and spare wheel.")
        case (.trunkToolkitHandOff, .openTrunk):
            trunkOpen = true
            feedback = "The trunk is open. Identify and grab each required tool."
        case (.trunkToolkitHandOff, .grabToolkit(let tool)):
            grabbedTools.insert(tool)
            if grabbedTools == Set(Tool.allCases) {
                advance(to: .assistedWheelChange, feedback: "Follow the five-point star pattern: 00 → 02 → 04 → 01 → 03.")
            } else {
                feedback = "Good. The remaining toolkit items are still in the spare well."
            }
        case (.assistedWheelChange, .crackLug(let index)):
            return crack(index)
        case (.assistedWheelChange, .positionJack):
            guard grabbedTools.contains(.scissorJack) else {
                return coach("Grab the scissor jack before positioning it at JACK_Point_RL.")
            }
            jackPositioned = true
            feedback = "Jack seated at the reinforced pinch-weld point. Crank until the tyre clears the ground."
        case (.assistedWheelChange, .crankJack):
            guard jackPositioned else { return coach("Position the jack at JACK_Point_RL first.") }
            jackRaised = true
            feedback = "Wheel is clear. Remove the five loosened nuts, then pull the flat wheel straight out."
        case (.assistedWheelChange, .removeWheel):
            guard jackRaised, crackedLugs.count == Self.starPattern.count else {
                return coach("Raise the jack and complete the star-pattern lug sequence first.")
            }
            flatWheelRemoved = true
            feedback = "Brake disc, caliper, and studs are visible. Mount the spare wheel."
        case (.assistedWheelChange, .mountSpare):
            guard flatWheelRemoved, grabbedTools.contains(.spareWheel) else {
                return coach("Remove the flat wheel and grab the spare wheel before mounting it.")
            }
            spareMounted = true
            feedback = "Spare mounted. Torque the nuts in the same five-point star order."
        case (.assistedWheelChange, .torqueLug(let index)):
            return torque(index)
        case (.assistedWheelChange, .lowerJack):
            guard spareMounted, torquedLugs.count == Self.starPattern.count else {
                return coach("Mount and torque the spare before lowering the jack.")
            }
            jackRaised = false
            advance(to: .recallChallenge, feedback: "Assisted repair complete. Try the 60-second recall challenge.")
        case (.recallChallenge, .beginRecall):
            resetForRecall()
            feedback = "Night scenario: no network. Secure the cockpit and recall the safe repair sequence."
        case (_, .requestHint):
            recallHintsUsed += 1
            feedback = hint
        default:
            return coach("That action is not safe or not needed yet.")
        }
        return true
    }

    public var hint: String {
        switch state {
        case .drivingIntro: return "Look for the mirror and HIGHWAY ASSISTANCE sign."
        case .tyreWarningPullOver: return "Steer smoothly to the shoulder before braking to a stop."
        case .secureCockpit: return "Park, parking brake, then hazards."
        case .mirrorCheckAndExit: return "Check passing traffic before opening the driver door."
        case .inspectFlatAndCall1033: return "Inspect the tyre, call 1033, then place the triangle."
        case .trunkToolkitHandOff: return "You need the lug wrench, scissor jack, and spare wheel."
        case .assistedWheelChange: return "Star order: 00 → 02 → 04 → 01 → 03."
        case .recallChallenge: return "Use the same safe order without relying on the mechanic."
        }
    }

    public func setTrafficDangerZoneOccupied(_ occupied: Bool) {
        trafficDangerZoneOccupied = occupied
        if occupied, state == .mirrorCheckAndExit {
            feedback = "Passing traffic is nearby. Check MIRROR_Driver and wait for a safe gap."
        }
    }

    @discardableResult
    private func crack(_ index: Int) -> Bool {
        guard grabbedTools.contains(.lugWrench) else {
            return coach("Grab the lug wrench before loosening a nut.")
        }
        guard Self.starPattern[safe: crackedLugs.count] == index else {
            return coach("Use the five-point star order: 00 → 02 → 04 → 01 → 03.")
        }
        crackedLugs.append(index)
        feedback = crackedLugs.count == Self.starPattern.count
            ? "All nuts are cracked. Position the jack at JACK_Point_RL."
            : "Nut \(index) loosened. Continue with the next star-pattern nut."
        return true
    }

    @discardableResult
    private func torque(_ index: Int) -> Bool {
        guard Self.starPattern[safe: torquedLugs.count] == index else {
            return coach("Torque the spare in the same star order.")
        }
        torquedLugs.append(index)
        feedback = torquedLugs.count == Self.starPattern.count
            ? "All nuts torqued. Lower the jack carefully."
            : "Nut \(index) torqued. Continue the star pattern."
        return true
    }

    private func advance(to next: State, feedback: String) {
        state = next
        self.feedback = feedback
    }

    @discardableResult
    private func coach(_ message: String) -> Bool {
        feedback = message
        return false
    }

    private func resetForRecall() {
        state = .recallChallenge
        procedureMode = nil
        hazardLampsActive = false
        driverDoorOpen = false
        trunkOpen = false
        jackPositioned = false
        jackRaised = false
        flatWheelRemoved = false
        spareMounted = false
        crackedLugs = []
        torquedLugs = []
        grabbedTools = []
        recallStep = 0
        trafficDangerZoneOccupied = false
        dialerConnected = false
    }

    private func isRecallControl(_ action: Action) -> Bool {
        if case .requestHint = action { return true }
        if case .beginRecall = action { return true }
        return false
    }

    private func handleRecall(_ action: Action) -> Bool {
        switch (recallStep, action) {
        case (0, .selectProcedure(let mode)):
            procedureMode = mode
            recallStep = 1
            feedback = "Procedure selected. Shift to Park."
        case (1, .shiftToPark):
            recallStep = 2
            feedback = "Park selected. Engage the parking brake."
        case (2, .engageParkingBrake):
            recallStep = 3
            feedback = "Parking brake engaged. Press hazards."
        case (3, .pressHazards):
            hazardLampsActive = true
            recallStep = 4
            feedback = "Hazards active. Check the driver mirror."
        case (4, .checkDriverMirror):
            recallStep = 5
            feedback = "Traffic gap confirmed. Open the driver door."
        case (5, .openDriverDoor):
            driverDoorOpen = true
            recallStep = 6
            feedback = "Inspect the flat tyre."
        case (6, .inspectFlatTyre):
            recallStep = 7
            feedback = "Call 1033."
        case (7, .call1033):
            recallStep = 8
            feedback = "Place the warning triangle."
        case (8, .placeWarningTriangle):
            recallStep = 9
            feedback = "Open the trunk."
        case (9, .openTrunk):
            trunkOpen = true
            recallStep = 10
            feedback = "Grab the lug wrench."
        case (10, .grabToolkit(.lugWrench)):
            grabbedTools.insert(.lugWrench)
            recallStep = 11
            feedback = "Grab the scissor jack."
        case (11, .grabToolkit(.scissorJack)):
            grabbedTools.insert(.scissorJack)
            recallStep = 12
            feedback = "Grab the spare wheel."
        case (12, .grabToolkit(.spareWheel)):
            grabbedTools.insert(.spareWheel)
            recallStep = 13
            feedback = "Crack lugs in star order: 00 → 02 → 04 → 01 → 03."
        case (13, .crackLug(let index)):
            guard Self.starPattern[safe: crackedLugs.count] == index else {
                return coach("Recall hint: use the five-point star order.")
            }
            crackedLugs.append(index)
            if crackedLugs.count == Self.starPattern.count {
                recallStep = 14
                feedback = "Position the jack at JACK_Point_RL."
            }
        case (14, .positionJack):
            jackPositioned = true
            recallStep = 15
            feedback = "Crank the jack until the wheel clears the ground."
        case (15, .crankJack):
            guard jackPositioned else { return coach("Position the jack first.") }
            jackRaised = true
            recallStep = 16
            feedback = "Remove the flat wheel."
        case (16, .removeWheel):
            guard jackRaised else { return coach("Raise the jack first.") }
            flatWheelRemoved = true
            recallStep = 17
            feedback = "Mount the spare wheel."
        case (17, .mountSpare):
            guard flatWheelRemoved else { return coach("Remove the flat wheel first.") }
            spareMounted = true
            recallStep = 18
            feedback = "Torque the spare in the same star order."
        case (18, .torqueLug(let index)):
            guard Self.starPattern[safe: torquedLugs.count] == index else {
                return coach("Recall hint: torque in the same star order.")
            }
            torquedLugs.append(index)
            if torquedLugs.count == Self.starPattern.count {
                recallStep = 19
                feedback = "Lower the jack carefully."
            }
        case (19, .lowerJack):
            jackRaised = false
            experienceCompleted = true
            totalElapsedSeconds = max(1, Int(Date().timeIntervalSince(experienceStartDate ?? Date())))
            safetyChecksPassed = 5
            feedback = "Recall challenge complete. You used the safe roadside sequence without network support."
        default:
            return coach("That action is out of order. Use a hint if needed.")
        }
        return true
    }

    private func resetExperience() {
        state = .drivingIntro
        procedureMode = nil
        feedback = "Observe the road, mirror, and HIGHWAY ASSISTANCE sign."
        hazardLampsActive = false
        driverDoorOpen = false
        trunkOpen = false
        jackPositioned = false
        jackRaised = false
        flatWheelRemoved = false
        spareMounted = false
        recallHintsUsed = 0
        crackedLugs = []
        torquedLugs = []
        grabbedTools = []
        recallStep = 0
        dialerConnected = false
        experienceStarted = false
        experienceCompleted = false
        totalElapsedSeconds = 0
        safetyChecksPassed = 0
        experienceStartDate = nil
    }
}

private extension Array {
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
