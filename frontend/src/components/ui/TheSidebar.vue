<template>
    <div class="d-flex flex-sm-column flex-row flex-nowrap bg-dark align-items-center sticky-top">
        <ul
            class="nav nav-pills nav-flush flex-sm-column flex-row flex-nowrap mb-auto mx-auto text-center align-items-center">
            <li class="nav-item">
                <a href="#" class="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right"
                    data-bs-original-title="Home">
                    <router-link to="/home">
                        <i class="bi-house fs-1"
                            :style="{ color: (currentRouteFullPath === '/home') ? 'rgb(16, 202, 240)' : null }">
                        </i>
                    </router-link>
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right"
                    data-bs-original-title="Energy">
                    <router-link to="/energy">
                        <i class="bi-lightning-fill fs-1"
                            :style="{ color: (currentRouteFullPath === '/energy') ? 'rgb(16, 202, 240)' : null }">
                        </i>
                    </router-link>
                </a>
            </li>
            <li>
                <a href="#" class="py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right"
                    data-bs-original-title="Heating">
                    <router-link to="/heating">
                        <i class="bi-fire fs-1"
                            :style="{ color: (currentRouteFullPath === '/heating') ? 'rgb(16, 202, 240)' : null }">
                        </i>
                    </router-link>
                </a>
            </li>
            <li>
                <a href="#" class="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right"
                    data-bs-original-title="Appliances">
                    <router-link to="/appliances">
                        <i class="bi-plug fs-1"
                            :style="{ color: (currentRouteFullPath === '/appliances') ? 'rgb(16, 202, 240)' : null }">
                        </i>
                    </router-link>
                </a>
            </li>
            <li>
                <a href="#" class="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right"
                    data-bs-original-title="Climate">
                    <router-link to="/climate">
                        <i class="bi-thermometer-half fs-1"
                            :style="{ color: (currentRouteFullPath === '/climate') ? 'rgb(16, 202, 240)' : null }">
                        </i>
                    </router-link>
                </a>
            </li>
            <li>
                <a href="#" class="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right"
                    data-bs-original-title="Charts">
                    <router-link to="/charts">
                        <i class="bi-graph-up fs-1"
                            :style="{ color: (currentRouteFullPath === '/charts') ? 'rgb(16, 202, 240)' : null }">
                        </i>
                    </router-link>
                </a>
            </li>
            <li class="dropdown">
                <a href="#" class="d-flex align-items-center justify-content-center p-3 link text-decoration-null"
                    id="dropdownUser3" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="bi-person-circle h2"></i>
                </a>
                <ul class="dropdown-menu text-small shadow" aria-labelledby="dropdownUser3">
                    <li><a class="dropdown-item" href="#">New project...</a></li>
                    <li><a class="dropdown-item" href="#">Settings</a></li>
                    <li><a class="dropdown-item" href="#">Profile</a></li>
                </ul>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    data() {
        return {
            currentRouteFullPath: '/'
        }
    },
    watch: {
        '$route'(to, from) {
            // This will be called whenever the route changes
            this.currentRouteFullPath = to.fullPath;
        }
    }
};
</script>