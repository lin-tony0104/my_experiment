import matplotlib.pyplot as plt


def count(imcome):
    tax=0
    if imcome>=0:
        temp=min(imcome,59)
        tax+=(temp-0)*0.05

    if imcome>=59:
        temp=min(imcome,133)
        tax+=(temp-59)*0.12

    if imcome>=133:
        temp=min(imcome,266)
        tax+=(temp-133)*0.2

    if imcome>=266:
        temp=min(imcome,498)
        tax+=(temp-266)*0.3

    if imcome>=498:
        temp=imcome
        tax+=(temp-498)*0.4

    return imcome-tax



total_income=100000#單位:萬
x=range(total_income)
y=[]
for i in range(total_income):
    y.append(count(i))


plt.plot(x,y)
plt.show()
