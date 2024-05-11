package ltd.newbee.mall.util;

import org.junit.Test;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class PythonUtil {


    public List<Long> runPythonScript(String pythonScriptPath, String arg) {
        String pythonHome = "D:\\Anaconda\\python.exe"; // 或者使用系统变量 "python"
        String[] command = {pythonHome, pythonScriptPath, arg};

        StringBuilder output = new StringBuilder();
        Process p;

        try {
            p = new ProcessBuilder(command).redirectErrorStream(true).start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            int exitCode = p.waitFor();
            if (exitCode != 0) {
                throw new RuntimeException("Python script exited abnormally!");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        String input=output.toString().trim();
        System.out.println(input);
        // 移除字符串两端的方括号
        input = input.substring(1, input.length() - 1);

        // 使用正则表达式匹配数字（包括逗号后的空格）
        Pattern pattern = Pattern.compile("\\s*\\d+\\s*(?=,|$)");
        Matcher matcher = pattern.matcher(input);
        List<Long> numbers = new ArrayList<>();

        while (matcher.find()) {
            // 将匹配到的数字转换为Long类型并添加到列表中
            numbers.add(Long.parseLong(matcher.group().trim()));
        }
        return numbers;
    }

    @Test
    public void testRunPythonScript()
    {
        String pythonScriptPath="D:\\研究生\\课程\\数据挖掘\\大作业\\newbee-mall-spring-boot-3.x\\newbee-mall-spring-boot-3.x\\src\\main\\java\\ltd\\newbee\\mall\\util\\main.py";
        String arg="2";
        //String res=runPythonScript(pythonScriptPath, arg);
        //System.out.println(res);
    }

}
