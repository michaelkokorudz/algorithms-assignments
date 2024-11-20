Name: Michael Kokorudz
Student Number: 20354593
netID = 21mek25


Comments for TA:
I utilized a min-heap holding the tuple of the triangles valence, unique identifier (id) and the triangle object itself. 
The min-heap was used for efficient access to the minimal valence triangles when starting a new strip. 
Removal from the min-heap is not required for triangles already on a strip, as they are skipped upon access. 
The algorithm then moves on to the next minimum valence triangle that is not part of any strip.
When a triangle is added to a strip, the valence of its neighbors is updated. 
Since the valence of a triangle can only decrease, the old version will not be accessed before the updated version due to the min-heap's properties.
This approach ensures a total algorithm time complexity of O(nlogn). 
The professor also stated the use of a min-heap was allowed and personally encouraged it. 