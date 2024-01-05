import { BaseService } from "@/services/base.js";

export class SilverService extends BaseService {
    constructor() {
        super("silver");
    }

    get_value_timestamp(queryParams) {
        return this.client.get(`${this.namespace}/value_timestamp`, { params: queryParams });
    }
}