import SwiftUI
#if os(visionOS)
import RealityKit
#endif

@main
struct BeyondSchoolApp: App {
    @State private var trainer = RoadsideTrainerModel()
    @State private var sceneController = RealitySceneController()

    var body: some SwiftUI.Scene {
        WindowGroup {
            TrainerView(model: trainer, sceneController: sceneController)
        }
    }
}

struct TrainerView: View {
    @Bindable var model: RoadsideTrainerModel
    let sceneController: RealitySceneController
    @State private var smoothCameraGlide = true
    @State private var subtitlesEnabled = true
    @State private var speechEnabled = true
    @State private var showingCompliance = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            if !model.experienceStarted {
                Text("Beyond School")
                    .font(.largeTitle.bold())
                Text("School teaches you what to know. Beyond School teaches you what to do.")
                    .font(.title3)
                    .foregroundStyle(.secondary)
                Button("Start 3-Minute Experience") {
                    _ = model.send(.startExperience)
                    sceneController.mechanicController.speak("Observe the road, mirror, and highway assistance sign.")
                }
                .buttonStyle(.borderedProminent)
                .accessibilityLabel("Start three minute roadside safety experience")
            } else {
                Text("Beyond School · Feature 01")
                    .font(.title.bold())
            }
            Text(model.state.rawValue.replacingOccurrences(of: "([a-z])([A-Z])", with: "$1 $2", options: .regularExpression).capitalized)
                .font(.title2.weight(.semibold))
            Text(model.feedback)
                .frame(maxWidth: .infinity, alignment: .leading)
            actionControls
            Toggle("Smooth camera glide", isOn: $smoothCameraGlide)
                .accessibilityLabel("Smooth camera glide")
            Toggle("English subtitles", isOn: $subtitlesEnabled)
                .accessibilityLabel("English subtitles")
            Toggle("Mechanic voice coach", isOn: $speechEnabled)
                .accessibilityLabel("Mechanic voice coach")
                .onChange(of: speechEnabled) { _, enabled in
                    sceneController.mechanicController.setSpeechEnabled(enabled)
                }
            Button("SSC credits and compliance") { showingCompliance = true }
                .accessibilityLabel("Open SSC credits and compliance sheet")
#if os(visionOS)
            RealitySceneSurface(model: model, sceneController: sceneController, smoothCameraGlide: smoothCameraGlide)
#endif
            if !sceneController.validationIssues.isEmpty {
                Text(sceneController.validationIssues.joined(separator: "\n"))
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            if model.experienceCompleted {
                scorecard
            }
        }
        .padding(24)
        .onChange(of: model.state) { _, newState in
            sceneController.synchronize(with: newState)
        }
        .task { await sceneController.loadScene() }
        .sheet(isPresented: $showingCompliance) {
            SSCComplianceSheet()
        }
    }

    @ViewBuilder
    private var actionControls: some View {
        switch model.state {
        case .drivingIntro:
            Button("Observe highway") {
                _ = model.send(.observeHighway)
                sceneController.mechanicController.speak("A tyre warning has appeared. Steer smoothly toward the shoulder.")
            }
        case .tyreWarningPullOver:
            HStack {
                Button("Steer to shoulder") { _ = model.send(.steerToShoulder) }
                Button("Brake to stop") { _ = model.send(.brakeToStop) }
            }
        case .secureCockpit:
            HStack {
                Button("Manual procedure") { _ = model.send(.selectProcedure(.manual)) }
                Button("Assisted procedure") { _ = model.send(.selectProcedure(.assisted)) }
                Button("Park") { _ = model.send(.shiftToPark) }
                Button("Parking brake") { _ = model.send(.engageParkingBrake) }
                Button("Hazards") { _ = model.send(.pressHazards) }
            }
        case .mirrorCheckAndExit:
            HStack {
                Button("Check mirror") { _ = model.send(.checkDriverMirror) }
                Button("Open driver door") {
                    model.setTrafficDangerZoneOccupied(sceneController.trafficController.isDangerZoneOccupied)
                    _ = model.send(.openDriverDoor)
                }
            }
        case .inspectFlatAndCall1033:
            HStack {
                Button("Inspect tyre") { _ = model.send(.inspectFlatTyre) }
                Button("Dial 1033") { _ = model.send(.dial1033) }
                Button("Place triangle") { _ = model.send(.placeWarningTriangle) }
            }
            VStack(alignment: .leading) {
                Text("HIGHWAY ASSISTANCE")
                    .font(.caption.bold())
                Text("NH-48 KM 142 · Left Shoulder")
                Text("••••  Signal · Offline GPS lock")
                Text(model.dialerConnected ? "Connected to National Highway Assistance" : "Ready to dial 1033")
                    .foregroundStyle(model.dialerConnected ? .green : .secondary)
            }
            .padding()
            .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
        case .trunkToolkitHandOff:
            HStack {
                Button("Open trunk") { _ = model.send(.openTrunk) }
                ForEach(RoadsideTrainerModel.Tool.allCases, id: \.self) { tool in
                    Button("Grab \(tool.rawValue)") { _ = model.send(.grabToolkit(tool)) }
                }
            }
        case .assistedWheelChange:
            HStack {
                ForEach(RoadsideTrainerModel.starPattern, id: \.self) { index in
                    Button("Lug \(index)") { _ = model.send(.crackLug(index)) }
                }
                Button("Position jack") { _ = model.send(.positionJack) }
                Button("Crank jack") { _ = model.send(.crankJack) }
                Button("Remove wheel") { _ = model.send(.removeWheel) }
                Button("Mount spare") { _ = model.send(.mountSpare) }
                Button("Lower jack") { _ = model.send(.lowerJack) }
            }
        case .recallChallenge:
            HStack {
                Button("Start recall challenge") { _ = model.send(.beginRecall) }
                Button("Hint") { _ = model.send(.requestHint) }
                Button("Manual") { _ = model.send(.selectProcedure(.manual)) }
                Button("Park") { _ = model.send(.shiftToPark) }
                Button("Brake") { _ = model.send(.engageParkingBrake) }
                Button("Hazards") { _ = model.send(.pressHazards) }
                Button("Mirror") { _ = model.send(.checkDriverMirror) }
                Button("Door") { _ = model.send(.openDriverDoor) }
                Button("Inspect") { _ = model.send(.inspectFlatTyre) }
                Button("1033") { _ = model.send(.call1033) }
                Button("Triangle") { _ = model.send(.placeWarningTriangle) }
                Button("Trunk") { _ = model.send(.openTrunk) }
            }
            if model.experienceCompleted {
                Button("Replay / Practice Again") { _ = model.send(.replayPractice) }
            }
            HStack {
                ForEach(RoadsideTrainerModel.starPattern, id: \.self) { index in
                    Button("Lug \(index)") { _ = model.send(.crackLug(index)) }
                }
                Button("Jack") { _ = model.send(.positionJack) }
                Button("Crank") { _ = model.send(.crankJack) }
                Button("Remove") { _ = model.send(.removeWheel) }
                Button("Spare") { _ = model.send(.mountSpare) }
                ForEach(RoadsideTrainerModel.starPattern, id: \.self) { index in
                    Button("Torque \(index)") { _ = model.send(.torqueLug(index)) }
                }
                Button("Lower") { _ = model.send(.lowerJack) }
            }
        }
    }

    private var scorecard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Mastery recap")
                .font(.title2.bold())
            Text("Safety checks passed: \(model.safetyChecksPassed)/5")
            Text("Star-pattern torque: \(model.torquedLugs.count == RoadsideTrainerModel.starPattern.count ? "Accurate" : "Review needed")")
            Text("Total time: \(model.totalElapsedSeconds)s · Target: ≤ 180s")
            Button("Replay / Practice Again") { _ = model.send(.replayPractice) }
                .buttonStyle(.borderedProminent)
        }
        .padding()
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Mastery recap. Safety checks passed \(model.safetyChecksPassed) of 5. Total time \(model.totalElapsedSeconds) seconds.")
    }
}

#if os(visionOS)
private struct RealitySceneSurface: View {
    @Bindable var model: RoadsideTrainerModel
    let sceneController: RealitySceneController
    let smoothCameraGlide: Bool

    var body: some View {
        RealityView { content, attachments in
            if let root = sceneController.root {
                content.add(root)
                if let callout = attachments.entity(for: "active-callout"),
                   let target = sceneController.entity(named: activeTargetName) {
                    callout.position = [0, 0.16, 0]
                    target.addChild(callout)
                }
                if let star = attachments.entity(for: "star-diagram"),
                   let target = sceneController.entity(named: "WHEEL_RL_FlatTarget") {
                    star.position = [0, 0.24, 0]
                    target.addChild(star)
                }
            }
        } attachments: {
            Attachment(id: "active-callout") {
                Text(model.feedback)
                    .font(.caption)
                    .padding(8)
                    .glassBackgroundEffect()
                    .accessibilityLabel("Training instruction")
            }
            Attachment(id: "star-diagram") {
                Text("00  →  02  →  04  →  01  →  03")
                    .font(.caption2.monospaced())
                    .padding(6)
                    .glassBackgroundEffect()
                    .accessibilityLabel("Five stud star torque order")
            }
        }
        .gesture(
            SpatialTapGesture()
                .targetedToAnyEntity()
                .onEnded { value in
                    guard let name = sceneController.resolveInteractiveName(from: value.entity) else { return }
                    _ = sceneController.tapEntity(named: name, model: model)
                }
        )
        .gesture(
            DragGesture(minimumDistance: 0)
                .targetedToAnyEntity()
                .onChanged { value in
                    guard let name = sceneController.resolveInteractiveName(from: value.entity) else { return }
                    let scale: Float = smoothCameraGlide ? 0.0005 : 0.001
                    sceneController.applyDrag(
                        to: name,
                        translation: [
                            Float(value.translation.width) * scale,
                            0,
                            Float(value.translation.height) * scale
                        ]
                    )
                }
        )
    }

    private var activeTargetName: String {
        switch model.state {
        case .secureCockpit: return "CTRL_ParkingBrake_Pivot"
        case .mirrorCheckAndExit: return "DOOR_DriverRight_Pivot"
        case .trunkToolkitHandOff: return "TRUNK_Lid_Pivot"
        case .assistedWheelChange: return "TOOL_LugWrench_Root"
        default: return "CONSOLE_GearSelector_Pivot"
        }
    }
}
#endif
