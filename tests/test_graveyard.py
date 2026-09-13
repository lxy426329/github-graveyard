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
    def test_empty(self):
        self.assertIn('nothing to bury',graveyard.render('test',[],30))
if __name__=='__main__': unittest.main()
