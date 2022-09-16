---
title: "Background Removal for Scanned Documents"
---

# {{ page.title }}

Often when scanning old documents, the page it was originally printed/written on has turned slightly yellowish, and it is not immediately cleanly reprintable. So we want to remove the background colour introduced by the page, while preserving the printed dark parts. Normally for text only documents this can be done by [simple thresholding, or adaptive thresholding](https://docs.opencv.org/3.4/d7/d4d/tutorial_py_thresholding.html), if the discolouration is uneven. The 
