Django Template Tag &mdash; Transmogrify v0.1beta2 documentation
# Django Template Tag #
<p>In the template, first:</p>
	{% load transmogrifiers %}
<p>You will have access to the following tags:</p>
* transmogrify
* thumbnail
* resize
* letterbox
* forcefit
* crop
* filter
* border

## transmogrify ##
<p>Alter an image URL so that the media server will transform the image on the
fly. This tag allows for multiple actions on an image. There are shortcuts for doing just one action.</p>
### Usage:
	{% transmogrify url [action [param]] [action2 [param2] ...] %}
### Available actions:
<b>thumbnail <width></b>
> Thumbnail to a given width. Height is set to maintain aspect ratio.

<b>thumbnail x<height></b>
> Thumbnail to a given height. Width is set to maintain aspect ratio.

<b>thumbnail <width>x<height></b>
> Thumbnail to fit a given size. The image is reduced to fit proportionally within the specified size.

<b>crop <width>x<height></b>
> Crop to a given size. Crops are centered within the image.

<b>resize <width>x<height></b>
> Resize the image proportionally to fit within the specified size.

<b>forcefit <width>x<height></b>
> Force the image to fit within the specified box; could result in a distorted image.

<b>letterbox <width>x<height> <color></b>
> Resize the image proportionally to fit within the specified size, and fill the remaining space with the specified color. Color should be in #RRGGBB or #RGB format.

<b>filter <filter></b>
> Run an image filter; filter can be:
* blur
* contour
* detail
* edge_enhance
* edge_enhance_more
* emboss
* find_edges
* smooth
* smooth_more
* sharpen
These don&#8217;t look all that good, but whatever.

<b>border <width> <color></b>
> Add a <width> pixel border around the image. <color> should be in HTML (#RRGGBB or #RGB) format.

### Examples:
<p>Thumbnail 200px wide:</p>
	{% transmogrify img thumbnail "200" %}
<p>Thumbnail 200px high:</p>
	{% transmogrify img thumbnail "x200" %}
<p>Thumbnail to fit within 200x200:</p>
	{% transmogrify img thumbnail "200x200" %}
<p>Resize to fit within a 400x400px box:</p>
	{% transmogrify img resize "400x400" %}
<p>Resize to be 400px wide:</p>
	{% transmogrify img resize "400" %}
<p>Resize to be 400px high:</p>
	{% transmogrify img resize "x400" %}
<p>Force the image to fit 75x75, distorting the image if the aspect isn&#8217;t right:</p>
	{% transmogrify img forcefit "75x75" %}
<p>Resize the image to fit 100x100 and sharpen:</p>
	{% transmogrify img resize "100x100" filter "sharpen" %}
<p>Resize the image to fit 100x100, smooth, and add a 1px black border:</p>
	{% transmogrify img resize "100x100" filter "smooth" border "1" "#000" %}
<p>Crop a 100x100 section out of the middle of image:</p>
	{% transmogrify img crop "100x100" %}


## thumbnail ##
<p>A shortcut to the transmogrify tag&#8217;s thumbnail action. It creates a thumbnail.</p>
### Usage:
	{% thumbnail <image_url> <width> %}
	{% thumbnail <image_url> x<height> %}
	{% thumbnail <image_url> <width>x<height> %}

### Examples:
<p>Thumbnail 200px wide</p>
	{% thumbnail img 200 %}
<img src="_images/horiz_img_t200.jpg" />
<img src="_images/square_img_t200.jpg" />
<img src="_images/vert_img_t200.jpg" />
<p>Thumbnail 200px high</p>
	{% thumbnail img x200 %}
<img src="_images/horiz_img_tx200.jpg" />
<img src="_images/square_img_tx200.jpg" />
<img src="_images/vert_img_tx200.jpg" />
<p>Thumbnail to fit within 200x200</p>
	{% thumbnail img 200x200 %}
<img src="_images/horiz_img_t200x200.jpg" />
<img src="_images/square_img_t200x200.jpg" />
<img src="_images/vert_img_t200x200.jpg" />


## resize ##
<p>A shortcut to the transmogrify tag&#8217;s resize action. It resizes the image to fit the dimensions and maintains the aspect ratio.</p>

### Usage:
	{% resize <image_url> <width> %}
	{% resize <image_url> x<height> %}
	{% resize <image_url> <width>x<height> %}

### Examples:
<p>Resize image to 500px wide</p>
	{% resize img 500 %}
<img src="_images/horiz_img_r500.jpg" />
<img src="_images/square_img_r500.jpg" />
<img src="_images/vert_img_r500.jpg" />
<p class="first admonition-title">Note</p>
<p class="last">The vertical image is not 500 pixels wide because the original is only 358 pixels wide. The Python Imaging Library will not upscale an image. Instead the original image is returned.</p>

<p>Resize image to 500px high</p>
	{% resize img x500 %}
<img src="_images/horiz_img_rx500.jpg" />
<img src="_images/square_img_rx500.jpg" />
<img src="_images/vert_img_rx500.jpg" />

<p>Resize image to fit within 500x500 pixel box</p>
	{% resize img 500x500 %}
<img src="_images/horiz_img_r500x500.jpg" />
<img src="_images/square_img_r500x500.jpg" />
<img src="_images/vert_img_r500x500.jpg" />


## letterbox ##
<p>A shortcut to the transmogrify tag&#8217;s letterbox action. It resizes the image to fit the dimensions and maintains the aspect ratio. The remaining space is filled with the color specified.</p>

### Usage:
	{% letterbox <image_url> <width>x<height> <color> %}

### Example:
<p>Resize image to fit within 500x500 pixel box, and fill the rest with red</p>
	{% letterbox img 500x500 #f00 %}
<img src="_images/horiz_img_l500x500-f00.jpg" />
<img src="_images/square_img_l500x500-f00.jpg" />
<img src="_images/vert_img_l500x500-f00.jpg" />

<p>Resize image to fit within 400x500 pixel box, and fill the rest with a light yellow</p>
	{% letterbox img 500x500 #fffee1 %}
<img src="_images/horiz_img_l500x500-fffee1.jpg" />
<img src="_images/square_img_l500x500-fffee1.jpg" />
<img src="_images/vert_img_l500x500-fffee1.jpg" />


## forcefit ##
<p>A shortcut to transmogrify tag&#8217;s forcefit action. It resizes the image to fit the dimensions, possibly distorting the image in the process.</p>

### Usage:
	{% forcefit <image_url> <width>x<height> %}

### Example:
<p>Resize image to fit within 300x300 pixel box</p>
	{% forcefit img 300x300 %}
<img src="_images/horiz_img_s300x300.jpg" />
<img src="_images/square_img_s300x300.jpg" />
<img src="_images/vert_img_s300x300.jpg" />


## crop ##
<p>A shortcut to the transmogrify tag&#8217;s crop action. It crops out a section of the center of an image.</p>

### Usage:
	{% crop <image_url> <width>x<height> %}

### Example:
<p>Crop a 100x100 section out of the middle of image</p>
	{% crop img 100x100 %}
<img src="_images/horiz_img_c100x100.jpg" />
<img src="_images/square_img_c100x100.jpg" />
<img src="_images/vert_img_c100x100.jpg" />


## filter ##
<p>A shortcut to the transmogrify tag&#8217;s filter action. It applies the specified filter (one of blur, contour, detail, edge_enhance, edge_enhance_more, emboss, find_edges, smooth, smooth_more, sharpen) to the image. Only one filter can be specified.</p>

### Usage:
	{% filter <image_url> <filtername> %}

### Examples:
<p>Blur</p>
<img src="_images/square_img_r300x300_fblur.jpg" />

<p>Contour</p>
<img src="_images/square_img_r300x300_fcontour.jpg" />

<p>Detail</p>
<img src="_images/square_img_r300x300_fdetail.jpg" />

<p>Edge Enhance</p>
<img src="_images/square_img_r300x300_fedge_enhance.jpg" />

<p>Edge Enhance More</p>
<img src="_images/square_img_r300x300_fedge_enhance_more.jpg" />

<p>Emboss</p>
<img src="_images/square_img_r300x300_femboss.jpg" />

<p>Find Edges</p>
<img src="_images/square_img_r300x300_ffind_edges.jpg" />

<p>Sharpen</p>
<img src="_images/square_img_r300x300_fsharpen.jpg" />

<p>Smooth</p>
<img src="_images/square_img_r300x300_fsmooth.jpg" />

<p>Smooth More</p>
<img src="_images/square_img_r300x300_fsmooth_more.jpg" />


## border ##
<p>A shortcut to the transmogrify tag&#8217;s border action. It applies a border of the specified width and color to the image.</p>

### Usage:
	{% border <image_url> <border_width> <color> %}

### Example:
<p>Add a 3 pixel light-yellow border around the image</p>
	{% border img 3 #fffee1 %}
<img src="_images/square_img_r300x300_b3-fffee1.jpg" />
