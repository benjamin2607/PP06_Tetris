import unittest

from Tetris import *

import xmlrunner 

class TetrisTest(unittest.TestCase):

  def testMove1(self):
    mehr = MehrsteinTetris()
    for _ in range(0,35): mehr.move()

    self.assertTrue(any([f!=background for f in mehr.grid[mehr.rows-1]]),"unterste Zeile nicht belegt, da sollten nich 25 move Steine liegen")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TetrisTest)
    xmlrunner.XMLTestRunner(output=".").run(suite)
    
  
