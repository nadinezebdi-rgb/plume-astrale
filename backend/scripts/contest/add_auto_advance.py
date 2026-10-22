"""Prend le v2 pptx et ajoute des timings auto-advance (10s/slide + loop)."""
from pptx import Presentation
from lxml import etree
from pptx.oxml.ns import qn

SRC = '/app/video_pitch_assets/Plume-Astrale-v2-source.pptx'
DST = '/app/frontend/public/demos/contest-deck-auto.pptx'

SECONDS_PER_SLIDE = 10

p = Presentation(SRC)

nsmap = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}

for slide in p.slides:
    xml = slide._element
    # Supprime tout <p:transition> existant pour éviter conflit
    for t in xml.findall(qn('p:transition')):
        xml.remove(t)
    # Ajoute <p:transition spd="med" advTm="10000"> + fade
    transition = etree.SubElement(
        xml, qn('p:transition'),
        attrib={'spd': 'med', 'advTm': str(SECONDS_PER_SLIDE * 1000)},
    )
    # Fade transition
    fade = etree.SubElement(transition, qn('p:fade'))
    # Ordre xml : transition doit être après timing, mais python-pptx accepte à la fin

# Loop infini : modifie <p:presentation> → <p:showPr loop="1"/>
pres_xml = p.part._element  # <p:presentation>
show_pr = pres_xml.find(qn('p:showPr'))
if show_pr is None:
    show_pr = etree.SubElement(pres_xml, qn('p:showPr'))
show_pr.set('loop', '1')
show_pr.set('useTimings', '1')

p.save(DST)
print(f'✅ PPTX auto-advance sauvegardé : {DST}')
print(f'   {len(p.slides)} slides · {SECONDS_PER_SLIDE}s/slide · loop infini')
