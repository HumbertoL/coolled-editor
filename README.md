# About

This app was created to preview and edit data on a 16x96 LED panel

# More Sample files

http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1696/data1696_static.json

http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1696/data1696_dynamic.json

See also

    private static final String UPDATE_JSON_FILE_URL_1248 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1248/";
    private static final String UPDATE_JSON_FILE_URL_1616 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1616/";
    private static final String UPDATE_JSON_FILE_URL_1632 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1632/";
    private static final String UPDATE_JSON_FILE_URL_1664 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1664/";
    private static final String UPDATE_JSON_FILE_URL_1696 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1696/";
    private static final String UPDATE_JSON_FILE_URL_3232 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/3232/";

        private static final String DYNAMIC_ANIMATION_FILE_NAME_1248 = "data1248_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_1616 = "data1616_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_1632 = "data1632_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_1664 = "data1664_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_1696 = "data1696_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_3232 = "data3232_dynamic.json";

# Data Format

This repo is using a reverse engineered data format that is used by the vendor.

Data is saved in .jt files. There's two types of files:

- Graffiti (static images)
- Animations

Both use essentially the same format.

Data is stored in a large array, split into individual bytes. For example:

```
[192, 15, 64, ...]
```

A static image with dimensions of 16x96 will have an array of 576 bytes. Note that this means each pixel is represented by 3 bits.

To interpret the data, first we convert each number in the array to an 8 bit binary number and build up a string.

```
110000001100000000001111000011110100000001000000...
```

Then we split the binary string into pieces that represent each column of pixels. Each column is 16 pixels tall and represented in 6 bytes.

```
11000000 11000000 00001111 00001111 01000000 01000000
```

We split the bytes representing the column into three evenly sized sections.

```
[1100000011000000, 0000111100001111, 0100000001000000]
```

For static image with dimensions of 16x96, there will be 96 columns, each 6 bytes. Each group represents one column.

These three parts of the group represent the red bits, the green bits and the blue bits.

So in this example, we take the first bit of each section:

| 1   | 0   | 0   |
| --- | --- | --- |
| R   | G   | B   |
| FF  | 00  | 00  |

This gives us the first pixel, which is the color #FF0000 aka red.

The second pixel is made up of the second bit in each array and so forth.

Each of those pixels is converted into a color in the same way:

| Binary | Hex    | Name    |
| ------ | ------ | ------- |
| 000    | 000000 | Black   |
| 001    | 0000FF | Blue    |
| 010    | 00FF00 | Green   |
| 011    | 00FFFF | Cyan    |
| 100    | FF0000 | Red     |
| 101    | FF00FF | Magenta |
| 110    | FFFF00 | Yellow  |
| 111    | FFFFFF | White   |

To convert the pixels to an image, we render starting at the top left, then moving down the column. Once the bottom of a column is reached, it starts at the top of the next column, like so:

| 1   | 4   | 7   |
| --- | --- | --- |
| 2   | 5   | 8   |
| 3   | 6   | 9   |

That'll look like:

| 100 | 000 | 010 |
| --- | --- | --- |
| 101 | 010 | 010 |
| 000 | 010 |     |

This process is continued using a height of 16 pixels and width of 96 pixels.

To represent multiple frames in an animation, each entire frame is stored in the binary data, one at a time:

[ `[576 bytes of frame 1 data]`, `[576 bytes of frame 2 data]`, `[576 bytes of frame 3 data]` ]

Note that the data is one continuous blob. Each frame is not an element in the array. We have to know to divide it up first, then process each subset of data with the process described above.
