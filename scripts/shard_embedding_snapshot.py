"""Losslessly shard a saved embedding snapshot for ordinary Git-sized artifacts."""
import argparse,gzip,hashlib,json,io
from pathlib import Path

def digest(b):return hashlib.sha256(b).hexdigest()
def shard(source):
    raw=source.read_bytes();decoded=gzip.decompress(raw);rows=json.loads(decoded)
    folder=source.parent/'embedding-snapshot-parts';folder.mkdir(exist_ok=False);parts=[]
    for i in range(0,len(rows),4096):
        content=json.dumps(rows[i:i+4096],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
        name=f'part-{i//4096:03d}.json.gz';data=gzip.compress(content,mtime=0);(folder/name).write_bytes(data)
        parts.append({'path':name,'rows':min(4096,len(rows)-i),'sha256':digest(data),'uncompressed_sha256':digest(content)})
    manifest={'rows':len(rows),'original_compressed_sha256':digest(raw),'original_uncompressed_sha256':digest(decoded),'original_path':source.name,'parts':parts,
              'note':'Lossless storage transformation only. Original concatenated array is reconstructed in part order; no new embedding calls or changed vector values.'}
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

def load(source):
    folder=source.parent/'embedding-snapshot-parts';manifest=json.loads((folder/'manifest.json').read_text());rows=[]
    for part in manifest['parts']:
        raw=(folder/part['path']).read_bytes()
        if digest(raw)!=part['sha256']:raise ValueError('part hash differs')
        decoded=gzip.decompress(raw)
        if digest(decoded)!=part['uncompressed_sha256']:raise ValueError('decoded part differs')
        rows.extend(json.loads(decoded))
    joined=json.dumps(rows,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    if len(rows)!=manifest['rows'] or digest(joined)!=manifest['original_uncompressed_sha256']:raise ValueError('reassembled snapshot differs')
    stream=io.BytesIO()
    with gzip.GzipFile(filename=manifest['original_path'][:-3],fileobj=stream,mode='wb',mtime=0) as z:z.write(joined)
    if digest(stream.getvalue())!=manifest['original_compressed_sha256']:raise ValueError('original compressed snapshot not reconstructed exactly')
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.verify:print(json.dumps({'rows_verified':len(load(a.source)),'fresh_api_calls':0}))
    else:
        m=shard(a.source);print(json.dumps({'rows':m['rows'],'parts':len(m['parts']),'sha256':m['original_uncompressed_sha256']}))
