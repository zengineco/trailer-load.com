import io,re,sys,glob
bad=0
for f in ['lock-in.html','index.html','privacy.html','terms.html','dashboard/index.html','me/index.html','ss/index.html','for-districts/index.html','for-districts/program-overview.html']:
    try: s=io.open(f,encoding='utf-8').read()
    except: continue
    if '<body' not in s: continue
    b=s[s.index('<body'):]
    b=re.sub(r'<script\b[^>]*>.*?</script>','',b,flags=re.S)
    b=re.sub(r'<style\b[^>]*>.*?</style>','',b,flags=re.S)
    b=re.sub(r'<!--.*?-->','',b,flags=re.S)
    for tag in ['div','span','button','label','p','section']:
        o=len(re.findall(r'<%s\b'%tag,b)); c=len(re.findall(r'</%s>'%tag,b))
        if o!=c:
            print('*** %s: <%s> open=%d close=%d delta=%+d'%(f,tag,o,c,c-o)); bad=1
print('DIV/TAG BALANCE: '+('*** BROKEN ***' if bad else 'ALL BALANCED'))
sys.exit(bad)
