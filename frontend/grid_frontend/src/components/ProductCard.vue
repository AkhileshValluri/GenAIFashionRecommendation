<template>
    <div class="product">
        <div class="box-content">
                <img :src="serverImgURL" class="image"/>
        </div>
        <div class="likebutton">
            <button @click="likeSubmit" :class="[isLiked ? 'liked' : 'notLiked']">{{like}}</button>
        </div>
    </div>
</template>

<script>
    export default {
        name : 'ProductCard',
        props:{
            url:String
        }, 
        data(){
            return{
                isLiked:false,
                like:'Like', 
                serverImgURL : 'http://127.0.0.1:5000/images/'+ this.url
            }
        },
        methods: {
            likeSubmit(){
                if(!this.isLiked){
                    this.isLiked = true;
                    this.like = 'Liked';
                }
                else{
                    this.isLiked = false;
                    this.like = 'Like'
                }
                console.log('Submitted');
            }
        }
    }
</script>

<style>
    .product{
        overflow: auto;
        background-color: gray;
        border-radius: 10px;
        border: 1px solid silver;
        flex: 0 0 calc(33.33% - 10px);
        height:50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .box-content {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1px;
        border-radius: 10px;
        margin-top: 4px;
        width: 40%;
        margin-left: auto;
        margin-right: auto;
  }

    .image{
        width:100%;
        height: 100%;
        scrollbar-width:thin;
        scrollbar-color: #e0e0e0 #f0f0f0;
    }

    .image::-webkit-scrollbar {
    width: 0px;
    background-color: grey;
    }

    .image::-webkit-scrollbar-thumb {
    background-color: white;
    border-radius: 0px;
    }

    .notLiked{
        border: none;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 5px;
        background-color: #007bff;
        width: 30%;
        margin-left:15vh;
        margin-right: 15vh;
        margin-top: 2%;
        cursor: pointer;
    }

    .liked{
        border: none;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 5px;
        background-color: yellowgreen;
        width: 30%;
        margin-left:15vh;
        margin-right: 15vh;
        margin-top: 2%;
        cursor: pointer;
    }
</style>
