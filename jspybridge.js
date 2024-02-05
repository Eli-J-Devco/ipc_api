

// console.log(process.argv);
var format = { language: 'sql', indent: '  ' };
function convert_mybatis(filename, namespace, id, param) {
    try {
        
    
    // console.log("filename: "+filename)
    // console.log("namespace: "+namespace)
    // console.log("id: "+id)
    // console.log("param: "+param)
    var mybatisMapper = require('mybatis-mapper');
    mybatisMapper.createMapper([filename]);
    let parameter 
    if (param.indexOf("'")) {
        parameter = JSON.parse(param.replaceAll("'", '"'), true);
    }
    else {
        parameter=param
    }
    
    var query = mybatisMapper.getStatement(namespace, id, parameter, format);
        console.log(query)
    } catch (error) {
        console.log(error);
    }
}
convert_mybatis(process.argv[3],process.argv[4],process.argv[5],process.argv[6])
