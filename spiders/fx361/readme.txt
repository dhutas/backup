数据格式：
1、文件名，为杂志名首字母，如《小小说月刊》为xxsyk.json，《故事会》为gsh.json。
2、期号，以2006年为例，是从20061到200612。
3、当该杂志某期号缺期时（该网站未收录此期杂志），"期号"该键存在，但值为空列表[]。
4、在期号下的列表是该期杂志每一篇文章，包含所属栏目，题目，作者，关键词，内容。
5、文章内容是以段落为项的列表。

文件名.json
{
    "期号":[{
        "l": "栏目",
        "t": "题目",
        "z": "作者",
        "k": ["关键词1","…"],
        "n": ["内容段落1","..."]}, {…} ]
}



