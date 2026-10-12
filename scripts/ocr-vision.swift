import Foundation
// Built for scripts/scan-social-claims.py:  swiftc -O scripts/ocr-vision.swift -o <scratch>/ocr
import Vision
import AppKit
// Usage: ocr <image>... → "file<TAB>x0,y0,x1,y1<TAB>text" (pixels, top-left origin)
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let w = Double(cg.width), h = Double(cg.height)
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    // Revision 3's Neural Engine path can fail on this machine (e5rt error 13); revision 2 (accurate) is reliable.
    req.revision = VNRecognizeTextRequestRevision2
    do {
        try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    } catch {
        FileHandle.standardError.write("ocr failed: \(path): \(error)\n".data(using: .utf8)!)
    }
    for obs in req.results ?? [] {
        guard let t = obs.topCandidates(1).first else { continue }
        let b = obs.boundingBox
        print("\(path)\t\(Int(b.minX*w)),\(Int((1-b.maxY)*h)),\(Int(b.maxX*w)),\(Int((1-b.minY)*h))\t\(t.string)")
    }
}
