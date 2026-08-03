// LOCK IN — WCAG CONTRAST AUDITOR (paste into the browser console on lock-in.html)
// Measures the REAL rendered contrast of every visible text node against its REAL
// effective background (walking ancestors past transparent fills). This is what a
// grep-based "legibility sweep" cannot do, and it is why v3.5.154 shipped a half-fix.
// Thresholds are WCAG AA: 4.5:1 normal text, 3:1 large text (>=18.66px, or >=14px bold).
(function(){
  function srgb(c){c/=255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4);}
  function lum(r,g,b){return .2126*srgb(r)+.7152*srgb(g)+.0722*srgb(b);}
  function parse(c){var m=(c||'').match(/rgba?\(([^)]+)\)/);if(!m)return null;
    var p=m[1].split(',').map(function(x){return parseFloat(x);});
    return {r:p[0],g:p[1],b:p[2],a:(p.length>3?p[3]:1)};}
  function over(fg,bg){ // alpha-composite fg over bg
    var a=fg.a;return {r:fg.r*a+bg.r*(1-a),g:fg.g*a+bg.g*(1-a),b:fg.b*a+bg.b*(1-a),a:1};}
  function effBg(el){
    var stack=[],n=el;
    while(n&&n.nodeType===1){var c=parse(getComputedStyle(n).backgroundColor);
      if(c&&c.a>0){stack.push(c); if(c.a>=1)break;} n=n.parentElement;}
    var base={r:255,g:255,b:255,a:1};
    for(var i=stack.length-1;i>=0;i--) base=over(stack[i],base);
    return base;
  }
  function ratio(a,b){var L1=lum(a.r,a.g,a.b),L2=lum(b.r,b.g,b.b);
    var hi=Math.max(L1,L2),lo=Math.min(L1,L2);return (hi+.05)/(lo+.05);}
  var out=[];
  [].slice.call(document.querySelectorAll('body *')).forEach(function(el){
    var cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||parseFloat(cs.opacity)===0)return;
    var r=el.getBoundingClientRect(); if(r.width<2||r.height<2)return;
    // direct text only (not inherited from children)
    var txt='';for(var i=0;i<el.childNodes.length;i++){var k=el.childNodes[i];
      if(k.nodeType===3)txt+=k.nodeValue;}
    txt=txt.replace(/\s+/g,' ').trim(); if(!txt)return;
    var fg=parse(cs.color); if(!fg)return;
    var bg=effBg(el); var fgc=fg.a<1?over(fg,bg):fg;
    var size=parseFloat(cs.fontSize), wt=parseInt(cs.fontWeight,10)||400;
    var large=(size>=18.66)||(size>=14&&wt>=700);
    var need=large?3:4.5, got=ratio(fgc,bg);
    if(got<need) out.push({txt:txt.slice(0,42),sel:(el.id?'#'+el.id:'.'+String(el.className).split(' ')[0]),
      ratio:Math.round(got*100)/100,need:need,size:Math.round(size),
      fg:cs.color,bg:'rgb('+Math.round(bg.r)+','+Math.round(bg.g)+','+Math.round(bg.b)+')'});
  });
  out.sort(function(a,b){return a.ratio-b.ratio;});
  return out;
})();
