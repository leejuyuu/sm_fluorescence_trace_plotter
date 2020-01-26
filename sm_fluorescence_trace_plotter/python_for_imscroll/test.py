import matplotlib.pyplot as plt
import numpy as np

plt.plot([1,2,3,4],[5,6,7,8],color = 'lightblue',linewidth=3)
plt.title('plot')
plt.xlabel('time')
plt.ylabel('intensity')
plt.show()

plt.savefig("test.png",Transparent = True , dpi = 600,bbox_inches='tight')
123
