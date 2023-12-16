// import welcome from '../sample/welcome_to_chaos_corner.json';
// import greenTopRight from '../sample/green_top_right.json';

function convertToBinary(num) {
    if (num < 0 || num > 255 || isNaN(num) || !Number.isInteger(num)) {
        return "Invalid input: Please provide a number between 0 and 255.";
    }

    return ('00000000' + num.toString(2)).slice(-8);
}


export const parseData = (content) => {
    const parsedJson = JSON.parse(content);
    const graffitiData = parsedJson[0].data.graffitiData;

    // combine into one string
    const binaryString = graffitiData.reduce(function (result, currentNum) {
        return result + convertToBinary(currentNum);
    }, '');

    return binaryString;
}