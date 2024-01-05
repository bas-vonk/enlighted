import { BaseService } from "@/services/base.js";

export class GoldService extends BaseService {
    constructor() {
        super("gold");
    }

    get_insight(queryParams) {
        return this.client.get(`${this.namespace}/insight`, { params: queryParams });
    }
}