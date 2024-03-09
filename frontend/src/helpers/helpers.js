export class TimeHelpers {
    static getHRFShort(unixTimestampSeconds) {
        return new Date(unixTimestampSeconds * 1000).toLocaleString(undefined, {
            month: "numeric", day: "numeric",
            hour: "numeric", minute: "numeric",
        })
    }

    static getHRFHoursMinutes(unixTimestampSeconds) {
        return new Date(unixTimestampSeconds * 1000).toLocaleString(undefined, {
            hour: "numeric", minute: "numeric",
        })
    }

    static getHRFLong(unixTimestampSeconds) {
        return new Date(unixTimestampSeconds * 1000).toLocaleString(undefined, {
            month: "numeric", day: "numeric",
            hour: "numeric", minute: "numeric",
            second: "numeric"
        })
    }

    static now() {
        return Math.floor(Date.now() / 1000)
    }

    static unixDaysInThePast(daysInThePast) {
        return this.now() - (3600 * 24 * daysInThePast)
    }
}

export class ArrayHelpers {
    static getLastItem(items) {
        return items[items.length - 1]
    }

    static getUniqueItemsSorted(items) {
        return [...new Set(items)].sort()
    }

    static makeSparse(items, factor) {
        return items.filter((_, index) => index % factor === 0)
    }
}