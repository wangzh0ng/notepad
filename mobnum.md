
dd={}
var  jsonp_queryMoreNums=function(data){
for(x=0;x<data.numArray.length/data.splitLen;x++)
{
nn = data.numArray[x*12]
if (dd[nn] == undefined && (nn+'').indexOf('4')==-1){
document.writeln(nn+'<br>');
dd[nn]=1
}
}
}


url ='https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_queryMoreNums&provinceCode=74&cityCode=744&monthFeeLimit=0&groupKey=71237034&searchCategory=3&net=01&amounts=200&codeTypeCode=&searchValue=&qryType=02&goodsNet=4&_=1526646216172'
xmlhttp=new XMLHttpRequest();
for(var y=0;y<10;y++){

xmlhttp.open("GET", url, false);
xmlhttp.send(null);
eval(xmlhttp.responseText)
console.log(y)
}
