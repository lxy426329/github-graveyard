import tempfile, unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import graveyard

class GraveyardTests(unittest.TestCase):
    def repo(self,name,days):
        pushed=(datetime.now(timezone.utc)-timedelta(days=days)).isoformat().replace('+00:00','Z')
        return {'name':name,'pushed_at':pushed,'html_url':'https://github.com/test/'+name,'fork':False,'archived':False}
    def test_threshold(self):
        svg=graveyard.render('test',[self.repo('alive',29),self.repo('dead',30)],30)
        self.assertNotIn('>alive<',svg); self.assertIn('>dead<',svg)
    def test_click_target_and_epitaph(self):
        svg=graveyard.render('test',[self.repo('old-project',365)],30)
        self.assertIn('<a href="https://github.com/test/old-project">',svg)
        self.assertIn('days quiet',svg); self.assertIn('class="flower"',svg)
        self.assertIn('†',svg); self.assertRegex(svg,r'\d{4}\.\d{2}\.\d{2}')
    def test_empty(self):
        self.assertIn('nothing to bury',graveyard.render('test',[],30))
    def test_archived_repo_is_clean_memorial(self):
        r=self.repo('finished',2); r['archived']=True
        svg=graveyard.render('test',[r],30)
        self.assertIn('archived · laid to rest',svg)
        self.assertIn('class="memorial"',svg)
        self.assertNotIn('class="plant"',svg)
        self.assertNotIn('days quiet',svg)
    def test_modes(self):
        inactive=self.repo('unfinished',40)
        archived=self.repo('finished',2); archived['archived']=True
        self.assertIn('>unfinished<',graveyard.render('test',[inactive,archived],mode='inactive'))
        self.assertNotIn('>finished<',graveyard.render('test',[inactive,archived],mode='inactive'))
        self.assertIn('>finished<',graveyard.render('test',[inactive,archived],mode='archived'))
        self.assertNotIn('>unfinished<',graveyard.render('test',[inactive,archived],mode='archived'))
    def test_exclude(self):
        svg=graveyard.render('test',[self.repo('private-ish',60)],exclude=['private-ish'])
        self.assertNotIn('>private-ish<',svg)
    def test_rows_override_limit(self):
        repos=[self.repo(f'dead-{i}',30+i) for i in range(10)]
        selected=graveyard.select_graves('test',repos,rows=1)
        self.assertEqual(4,len(selected))
    def test_recent_resurrection_leaves_sprout(self):
        today=datetime.now(timezone.utc).date().isoformat()
        history={'ghost':{'burials':1,'resurrections':1,'buried':False,'events':[{'type':'resurrected','at':today}]}}
        svg=graveyard.render('test',[],30,history=history)
        self.assertIn('ghost · resurrected 0d',svg)
        self.assertIn('class="sprout"',svg)
    def test_second_burial_marks_grave(self):
        history={'dead':{'burials':2,'resurrections':1,'buried':True,'events':[]}}
        svg=graveyard.render('test',[self.repo('dead',31)],30,history=history)
        self.assertIn('· Ⅱ',svg)
if __name__=='__main__': unittest.main()
