export function getCommaSeparatedValues(line : string) : string[] {
    const values = [];
    let insideQuotes : boolean = false;

    let subToken = ""
    for (let i = 0; i < line.length; ++i) {
        const letter = line.at(i);
        if (letter === "\"") {
            insideQuotes = !insideQuotes;
        } else if (letter === "," && !insideQuotes) {
            values.push(subToken);
            subToken = "";
        } else {
            subToken += letter;
        }
    }
    values.push(subToken);
    return values;
}