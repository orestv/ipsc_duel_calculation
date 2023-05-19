const APPDIR = 'src/'

const path = require('path');
const HtmlWebpackPlugin = require("html-webpack-plugin");
const HTMLWebpackPluginConfig = new HtmlWebpackPlugin({
    template: 'src/index.html',
    filename: 'index.html',
    inject: 'body'
});

module.exports = {
    entry: './src/index.tsx',
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
    },
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist'),
    },
    plugins: [
        HTMLWebpackPluginConfig
    ],
    devServer: {
        static: path.join(__dirname, "dist"),
        port: 4000,
        compress: true,
        watchFiles: ["./src/*"],
        proxy: {
            '/duels': 'http://localhost:4200'
        }
    },
    devtool: 'source-map'
};
