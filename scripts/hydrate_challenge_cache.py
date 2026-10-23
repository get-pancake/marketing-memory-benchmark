"""Create an external SQLite embedding cache from public lossless snapshot parts."""
import argparse,base64,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.shard_embedding_snapshot import load

def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('use a new cache output')
    a.output.parent.mkdir(parents=True,exist_ok=True);rows=load(a.snapshot);db=sqlite3.connect(a.output)
    db.execute('CREATE TABLE embeddings(text TEXT PRIMARY KEY,vector BLOB,origin TEXT)')
    for r in rows:
        value=base64.b64decode(r['vector_base64'])
        if len(value)!=4096:raise ValueError('wrong vector dimensions')
        db.execute('INSERT INTO embeddings VALUES (?,?,?)',(r['text'],value,r['origin']))
    db.commit();db.close();print(f'Cached {len(rows)} actual saved embeddings; no API calls.')

if __name__=='__main__':main()
