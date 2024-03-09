<template>
    <div class="container-fluid pt-2 px-4 h-100">
        <div class="row">
            <div class="col-md-6">
                <base-card>
                    <template v-slot:header>Welcome</template>
                    <template v-slot:body>
                        <div style="padding: 2rem;">
                            To the Enlighted app.
                        </div>
                    </template>
                </base-card>
            </div>

        </div>
    </div>
</template>

<script lang="js">
import BaseCard from '@/components/ui/BaseCard.vue'


export default {
    name: 'HomeDashboardView',
    components: { BaseCard },
}
</script>

<style></style>
