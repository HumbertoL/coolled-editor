export const colors = [
    { name: 'Black', hex: '#000000' },
    { name: 'Red', hex: '#FF0000' },
    { name: 'Pink', hex: '#FF00FF' },
    { name: 'Yellow', hex: '#FFFF00' },
    { name: 'Green', hex: '#00FF00' },
    { name: 'Cyan', hex: '#00FFFF' },
    { name: 'Blue', hex: '#0000FF' },
    { name: 'White', hex: '#FFFFFF' },
];

// const getNameFromHex = (hex) => {
//     const color = colors.find((color) => color.hex === hex);
//     return color ? color.name : 'None';
// }

export const getColorObjectFromName = (name) => {
    
    const color = colors.find((color) => color.name === name)
    const hexCode = color.hex;
    // remove #
    const hex = hexCode.substring(1);
    // convert to rgb
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    return { r, g, b };

}

export const getColorFromChunk = (pixel) => {
    const { r, g, b } = pixel;
    const redValue = r ? 'FF' : '00';
    const greenValue = g ? 'FF' : '00';
    const blueValue = b ? 'FF' : '00';

    return `#${redValue}${greenValue}${blueValue}`
}
 