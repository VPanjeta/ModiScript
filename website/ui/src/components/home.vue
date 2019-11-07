<template>
  <v-container class="text-center mt-10">
    <h2 class="display-2 font-weight-bold">
      ModiScript
    </h2>
    <p class="display-1">
      For the Next Billion Indians!
    </p>

    <v-row justify="center">
      <v-col class="d-flex" cols="12">
        <v-select
          :items="options"
          item-text="name"
          item-value="value"
          filled
          label="Select a Program"
          dense
          v-model="choice"
        ></v-select>
      </v-col>
      <v-col class="d-flex" cols="12">
        <v-textarea
          filled
          name="input-7-4"
          label="Code"
          v-model="code"
        ></v-textarea>
      </v-col>
      <v-col class="d-flex" cols="12">
        <v-textarea
          filled
          name="input-7-4"
          label="Input (STDIN)"
          v-model="stdin"
        ></v-textarea>
      </v-col>

      <v-btn @click="submit" large color="primary">Submit</v-btn>
      <v-col class="d-flex" cols="12">
        <v-textarea
          name="input-7-4"
          label="Output"
          readonly
          v-model="out"
        ></v-textarea>
      </v-col>

    </v-row>
    <p class="headline">
      Created By The 
      <a href="https://github.com/VPanjeta/ModiScript">
        ModiScript Team 
      </a>.
    </p>
  </v-container>
</template>

<script>
import codes from '../codes'
import axios from 'axios'
export default {
  name: "home",
  data() {
    return {
      stdin: "",
      code: "",
      choice: "",
      options: [
        { name: "Hello World", value: "hello-world" },
        { name: "Agar / Nahi Toh (If / Else)", value: "if-else" },
        { name: "Mandir.chai", value: "mandir" },
        { name: "Scam.chai", value: "scam" },
        { name: "Factorial.chai", value: "factorial" },
        { name: "Custom", value: "custom" }
      ],
      out: "" 
    }
  },
  methods: {
    submit() {
      let obj = { code: this.code }
      if (this.stdin) {
        obj.stdin = this.stdin;
      }
      axios.post("https://modiscript.daksh.now.sh/", obj)
        .then(res => this.out = res.data.out)
        .catch(err => this.out = err.response.data.error)
    }
  },
  watch: {
    choice(v) {
      this.code = codes[v];
    }
  },
  mounted() {
    this.choice = "hello-world"
  }
}
</script>
