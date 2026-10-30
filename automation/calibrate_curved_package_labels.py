"""Local-only reproducible three-angle caption calibration; no API or publication."""
import hashlib,io,json
from pathlib import Path
from PIL import Image
import blog_package_labels as labels
ROOT=Path(__file__).resolve().parents[1]
CASES={'holdout':'41037090356/case-3-native.webp','baseline':'41029742464/case-2-candidate-v2.webp','angle':'41031355848/case-2-finish-edit.webp'}
def main():
 out=ROOT/'artifacts/blog-image-calibration/cylindrical-faraparsian-v2';out.mkdir(parents=True,exist_ok=True)
 report={'policy':labels.POLICY,'canonical_persian':labels.PERSIAN,'canonical_english':labels.ENGLISH,'scope':'local geometry and typography only; no independent online OCR or full-image approval','production_activated':False,'new_image_requests':0,'post_submissions':0,'cases':[]}
 for name,path in CASES.items():
  raw=(ROOT/'artifacts/blog-image-calibration'/path).read_bytes();im,proof=labels.typeset(raw,labels.detect_geometry(raw));target=out/(name+'.webp');im.save(target,'WEBP',quality=95,method=6)
  report['cases'].append({'case':name,'source_path':'artifacts/blog-image-calibration/'+path,'output_path':str(target.relative_to(ROOT)),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'typesetting':proof})
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
