<script setup lang="ts">

</script>

<template> 
    <section>
        <h1>LOGIN</h1>

        <form>
            <div>
                <label for="email">Email</label>
                <input id="email" type="email" />
            </div>
            <div>
                <label for="password">Password</label>
                <input id="password" type="password" />
            </div>
            <!-- Dummy Invalid Creds -->
             <button type="submit">
                Login
             </button>

             <button type="button">
                Register
             </button>
        </form>
    </section>

</template>