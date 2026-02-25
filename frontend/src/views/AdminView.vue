<script setup lang="ts">
import AppNavbar from '@/components/common/AppNavbar.vue'
import AnimatedBackground from '@/components/animations/AnimatedBackground.vue'
import UserManagementTable from '@/components/admin/UserManagementTable.vue'
import AdminStatsOverview from '@/components/admin/AdminStatsOverview.vue'
</script>

<template>
  <div class="relative flex min-h-screen flex-col overflow-x-hidden">
    <AnimatedBackground />
    <AppNavbar />
    
    <main class="flex-1 w-full relative z-10 px-4 py-8 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl space-y-8">
        <div>
          <h1 class="text-3xl font-bold tracking-tight bg-gradient-to-r from-teal-500 to-cyan-500 bg-clip-text text-transparent">Admin Dashboard</h1>
          <p class="mt-2 text-muted-foreground">
            Manage users, view platform usage, and administer the Medible platform.
          </p>
        </div>
        
        <AdminStatsOverview />
        <UserManagementTable />
      </div>
    </main>
  </div>
</template>
