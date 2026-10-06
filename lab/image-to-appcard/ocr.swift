import Foundation
import Vision
import AppKit
let url=URL(fileURLWithPath:CommandLine.arguments[1])
let image=NSImage(contentsOf:url)!
var rect=CGRect(origin:.zero,size:image.size)
let cg=image.cgImage(forProposedRect:&rect,context:nil,hints:nil)!
let request=VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false
request.recognitionLanguages=["zh-Hans", "en-US"]
try VNImageRequestHandler(cgImage:cg).perform([request])
let rows=(request.results ?? []).compactMap { row -> [String:Any]? in
 guard let text=row.topCandidates(1).first else{return nil}
 let b=row.boundingBox
 return ["text":text.string,"confidence":text.confidence,"bounds":[b.minX*Double(cg.width),(1-b.maxY)*Double(cg.height),b.width*Double(cg.width),b.height*Double(cg.height)]]
}
let result:[String:Any] = ["width":cg.width,"height":cg.height,"observations":rows]
let data=try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys])
FileHandle.standardOutput.write(data)
